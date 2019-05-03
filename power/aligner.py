from __future__ import division
from collections import deque
from power.levenshtein import Levenshtein, ExpandedAlignment, AlignLabels
from power.phonemes import Phonemes
from power.pronounce import PronouncerType, PronouncerBase, PronouncerLex

class TokType:
    WordBoundary = 1
    SyllableBoundary = 2
    Phoneme = 3
    Empty = 0
    
    @staticmethod
    def checkAnnotation(tok):
        tt = TokType.Phoneme
        if not tok:
            tt = TokType.Empty
        elif tok == '|':
            tt = TokType.WordBoundary
        elif tok == '#':
            tt = TokType.SyllableBoundary
        return tt
    
class CharToWordAligner:
    def __init__(self, ref, hyp, lowercase=False):
        self.refwords = ref.strip()
        self.hypwords = hyp.strip()
        self.ref = ref
        self.hyp = hyp
        self.lowercase = lowercase
        self.char_align = None
        self.word_align = None
        
    def charAlign(self):
        ref_chars = [x for x in self.ref] + [' ']
        hyp_chars = [x for x in self.hyp] + [' ']
        
        lev = Levenshtein.align(ref_chars, hyp_chars, lowercase=self.lowercase, reserve_list=set([' ']))
        lev.editops()
        self.char_align = lev.expandAlign()
        return self.char_align
        
    def charAlignToWordAlign(self):
        if not self.char_align:
            raise Exception("char_align is None")
        
        ref_word_align = []
        hyp_word_align = []
        align_word = []
        
        tmp_ref_word = []
        tmp_hyp_word = []
        
        for i in range(len(self.char_align.align)):
            ref_char = self.char_align.s1[i]
            hyp_char = self.char_align.s2[i]
            align_char = self.char_align.align[i] 

            # check if both words are completed
            # There are a few of ways this could happen:
            if ((align_char == AlignLabels.correct and ref_char == ' ') or
                (align_char == AlignLabels.deletion and ref_char == ' ') or
                (align_char == AlignLabels.insertion and hyp_char == ' ')):

                ref_word = ''.join(tmp_ref_word)
                hyp_word = ''.join(tmp_hyp_word)
                
                if ref_word or hyp_word:
                    ref_word_align.append(ref_word)
                    hyp_word_align.append(hyp_word)
                    tmp_ref_word = []
                    tmp_hyp_word = []
                    
                    # Check align type
                    if ref_word and hyp_word:
                        if ref_word == hyp_word:
                            align_word.append(AlignLabels.correct)
                        else:
                            align_word.append(AlignLabels.substitution)
                    elif ref_word:
                        align_word.append(AlignLabels.deletion)
                    else:
                        align_word.append(AlignLabels.insertion)
                continue
            
            # Read current chars and check if one of the words is complete
            if ref_char == ' ':
                if len(tmp_ref_word) > 1:
                    # Probably a D
                    ref_word = ''.join(tmp_ref_word)
                    ref_word_align.append(ref_word)
                    hyp_word_align.append('')
                    tmp_ref_word = []
                    align_word.append(AlignLabels.deletion)
            else:
                tmp_ref_word.append(ref_char)
            
            if hyp_char == ' ':
                if len(tmp_hyp_word) > 1:
                    # Probably an I
                    hyp_word = ''.join(tmp_hyp_word)
                    ref_word_align.append('')
                    hyp_word_align.append(hyp_word)
                    tmp_hyp_word = []
                    align_word.append(AlignLabels.insertion)
            else:
                tmp_hyp_word.append(hyp_char)
            
        self.word_align = ExpandedAlignment(ref_word_align, hyp_word_align, align_word, lowercase=self.lowercase)
        return self.word_align	
            
class PowerAligner:
    # Exclusive tokens that can only align to themselves; not other members in this set.
    reserve_list = set(['|', '#'])
    
    # R-sounds
    r_set = set.union(set('r'), Phonemes.r_vowels)
    exclusive_sets = [Phonemes.vowels, Phonemes.consonants, r_set]
    
    phoneDistPenalty    = 0.25
    phoneDistPenalt16ySet = set(['|'])
    
    def __init__(self, ref, hyp, lowercase=False, verbose=False,
                pronounce_type=PronouncerType.Lexicon,
                lexicon=None,
                word_align_weights=Levenshtein.wordAlignWeights):
        if not ref:
            raise Exception("No reference file.\nref: {0}\nhyp: {1}".format(ref, hyp))

        if pronounce_type == PronouncerType.Lexicon:
            self.pronouncer = PronouncerLex(lexicon)
        else:
            self.pronouncer = PronouncerBase()
        
        self.ref = [x for x in ref.strip().split() if x]
        self.hyp = [x for x in hyp.strip().split() if x]
        self.refwords = ' '.join(self.ref)
        self.hypwords = ' '.join(self.hyp)
        
        self.lowercase = lowercase
        self.verbose = verbose
        
        # Perform word alignment
        lev = Levenshtein.align(self.ref, self.hyp, lowercase=self.lowercase, weights=word_align_weights)
        lev.editops()
        self.wer_alignment = lev.expandAlign()
        self.wer, self.wer_components = self.wer_alignment.error_rate()
        
        # Used for POWER alignment
        self.power_alignment = None
        self.power = None
        self.power_components = None
        
        # Used to find potential error regions
        self.split_regions = None
        self.error_indexes = None
        self.phonetic_alignments = None
        self.phonetic_lev = None
        
    def align(self):
        # Find the error regions that may need to be realigned
        self.split_regions, self.error_indexes = self.wer_alignment.split_error_regions()
        self.phonetic_alignments = [None] * len(self.split_regions)

        for error_index in self.error_indexes:
            seg = self.split_regions[error_index]
            ref_words = seg.s1_tokens()
            hyp_words = seg.s2_tokens()
            ref_phones = self.pronouncer.pronounce(ref_words)
            hyp_phones = self.pronouncer.pronounce(hyp_words)

            print('REF', ref_phones)
            print('HYP', hyp_phones)

            power_seg_alignment, self.phonetic_alignments[error_index] = PowerAligner.phoneAlignToWordAlign(ref_words, hyp_words, 
                ref_phones, hyp_phones)

            print(self.phonetic_alignments[error_index])

            # Replace the error region at the current index.
            self.split_regions[error_index] = power_seg_alignment

        # Merge the alignment segments back together.
        self.power_alignment = ExpandedAlignment(self.split_regions[0].s1, self.split_regions[0].s2, 
                self.split_regions[0].align, 
                self.split_regions[0].s1_map, self.split_regions[0].s2_map, lowercase=self.lowercase)
        for i in range(1, len(self.split_regions)):
            self.power_alignment.append_alignment(self.split_regions[i])
        
        # Get the alignment score
        self.power, self.power_components = self.power_alignment.error_rate()
                
        assert self.hypwords == self.power_alignment.s2_string(), "hyp mismatch:\n{0}\n{1}".format(self.hypwords, self.power_alignment.s2_string())
        assert self.refwords == self.power_alignment.s1_string(), "ref mismatch:\n{0}\n{1}".format(self.refwords, self.power_alignment.s1_string())
  
    # TODO: Make this simpler (and maybe recursive)
    @classmethod
    def phoneAlignToWordAlign(cls, ref_words, hyp_words, ref_phones, hyp_phones, break_on_syllables=True):
        ref_word_span = (0, len(ref_words))
        hyp_word_span = (0, len(hyp_words))
        
        # Perform Levenshtein Alignment
        lev = Levenshtein.align(ref=ref_phones, 
                            hyp=hyp_phones,
                            reserve_list=PowerAligner.reserve_list, 
                            exclusive_sets=PowerAligner.exclusive_sets,
                            weights=Levenshtein.wordAlignWeights) #, 
                            #dist_penalty=PowerAligner.phoneDistPenalty, dist_penalty_set=Levenshtein.wordAlignWeights)				
        phone_align = lev.expandAlignCompact()
        
        worklist = list()
        worklist.append((ref_word_span, hyp_word_span, phone_align))
        
        full_reference = list()
        full_hypothesis = list()
        full_alignment = list()
        full_phone_align = list()
        
        while worklist:
            # Take the next set of sequence boundaries off the worklist
            ref_word_span, hyp_word_span, phone_align = worklist.pop()
            ref_word_index, ref_word_limit = ref_word_span
            hyp_word_index, hyp_word_limit = hyp_word_span
            
            # TODO: Currently only checking in the forward direction
            ref_word_builder = []  # Temp storage of words in alignment span
            hyp_word_builder = []
            
            ref_word_iter = enumerate(ref_words[ref_word_span[0]:ref_word_span[1]])  # Iterates through the surface words
            hyp_word_iter = enumerate(hyp_words[hyp_word_span[0]:hyp_word_span[1]])
            
            ref_aligned = []  # Finalized alignments
            hyp_aligned = []
            alignment = []  # Finalized alignment labels
            
            ref_extra_syllable_word_index = None  # Used for marking words mapping to extra syllables in alignment.
            hyp_extra_syllable_word_index = None
            ref_syllable_count = 0
            hyp_syllable_count = 0
        
            ref_word_started = False  # Indicates whether a word is already accounted for in the alignment when a phoneme is reached.
            hyp_word_started = False
            
            advance_worklist = False
            commit_alignment = False
            
            for i in range(len(phone_align.align)):
                ref_type = TokType.checkAnnotation(phone_align.s1[i])
                hyp_type = TokType.checkAnnotation(phone_align.s2[i])
                
                # Check if word boundaries are reached, both on ref an hyp -- or the case where no more symbols can be read.
                if (i == len(phone_align.align) - 1) or (ref_type == TokType.WordBoundary and ref_type == hyp_type):
                    align_tok = None
                    # Only write outputs if either the ref or the hyp has scanned some words.
                    if ref_word_builder:
                        if hyp_word_builder:
                            align_tok = AlignLabels.substitution if ref_word_builder != hyp_word_builder else AlignLabels.correct
                        else:
                            align_tok = AlignLabels.deletion
                    elif hyp_word_builder:
                        align_tok = AlignLabels.insertion
    
                    if align_tok:
                        # Add the remainder to the worklist
                        ref_word_span_next = (ref_word_index + len(ref_word_builder), ref_word_limit)
                        hyp_word_span_next = (hyp_word_index + len(hyp_word_builder), hyp_word_limit)
                        phone_align_next = phone_align.subsequence(i, phone_align.length(), preserve_index=False)
                        worklist.append((ref_word_span_next, hyp_word_span_next, phone_align_next))
                        
                        # "Commit" the current alignment
                        if align_tok in (AlignLabels.correct, AlignLabels.substitution):
                            alignment.append(align_tok)
                            
                            # Check for syllable conflicts
                            if not break_on_syllables or not ref_extra_syllable_word_index:
                                ref_aligned.append(' '.join(ref_word_builder))
                                ref_syllable_count = 0
                                hyp_syllable_count = 0
                            else:
                                ref_aligned.append(' '.join(ref_word_builder[0:ref_extra_syllable_word_index]))
                                # The remaining words are deletions
                                for word in ref_word_builder[ref_extra_syllable_word_index:]:
                                    alignment.append(AlignLabels.deletion)
                                    ref_aligned.append(word)
                                    hyp_aligned.append('')
                                ref_syllable_count = 0
                                
                            if not break_on_syllables or not hyp_extra_syllable_word_index:
                                hyp_aligned.append(' '.join(hyp_word_builder))
                                ref_syllable_count = 0
                                hyp_syllable_count = 0
                            else:
                                hyp_aligned.append(' '.join(hyp_word_builder[0:hyp_extra_syllable_word_index]))
                                # The remaining words are insertions
                                for word in hyp_word_builder[hyp_extra_syllable_word_index:]:
                                    alignment.append(AlignLabels.insertion)
                                    ref_aligned.append('')
                                    hyp_aligned.append(word)
                                    hyp_syllable_count = 0
                            
                            if align_tok == AlignLabels.substitution:
                                # Check if you need to rework this alignment.
                                if len(ref_word_builder) != len(hyp_word_builder):
                                    # Word count mismatch in the alignment span. Is there a possibility that we need to re-align this segment?
                                    ref_word_span_curr = (ref_word_index, ref_word_index + len(ref_word_builder))
                                    hyp_word_span_curr = (hyp_word_index, hyp_word_index + len(hyp_word_builder))
                                    phone_align_curr = phone_align.subsequence(0, i+1, preserve_index=False)
                                    
                                    lev = Levenshtein.align(
                                        ref=phone_align_curr.s1_tokens(), 
                                        hyp=phone_align_curr.s2_tokens(),
                                        reserve_list=PowerAligner.reserve_list, 
                                        exclusive_sets=PowerAligner.exclusive_sets,
                                        weights=Levenshtein.wordAlignWeights) #, 
                                        #dist_penalty=PowerAligner.phoneDistPenalty, dist_penalty_set=Levenshtein.wordAlignWeights)
                                        
                                    phone_align_adjusted = lev.expandAlignCompact()
                                    
                                    if phone_align_curr.align != phone_align_adjusted.align:
                                        # Looks like we need to redo the phone-to-word alignment.
                                        worklist.append((ref_word_span_curr, hyp_word_span_curr, phone_align_adjusted))
                                    else:
                                        commit_alignment = True
                                else:
                                    commit_alignment = True
                                        
                        elif align_tok == AlignLabels.deletion:
                            for word in ref_word_builder:
                                alignment.append(align_tok)
                                ref_aligned.append(word)
                                hyp_aligned.append('')
                                
                            commit_alignment = True
                            ref_syllable_count = 0
                            
                        elif align_tok == AlignLabels.insertion:
                            for word in hyp_word_builder:
                                alignment.append(align_tok)
                                ref_aligned.append('')
                                hyp_aligned.append(word)
                                        
                            commit_alignment = True
                            hyp_syllable_count = 0
                            
                        if commit_alignment:
                            # Commit the alignment.
                            full_reference.extend(ref_aligned)
                            full_hypothesis.extend(hyp_aligned)
                            full_alignment.extend(alignment)
                            full_phone_align.append(phone_align.subsequence(0, i, preserve_index=False))
                            ref_aligned = []
                            hyp_aligned = []
                            alignment = []
                        break
                
                # Add words if word boundaries are reached.
                else:
                    if ref_type == TokType.WordBoundary:
                        ref_word_started = False
                        if hyp_type != TokType.WordBoundary and ref_word_builder and not hyp_word_builder:
                            # DELETION
                            # Ref word ended, but no hyp words have been added. Mark the current ref word(s) in the span as deletion errors.
                            # TODO: Dedupe this logic
                            for word in ref_word_builder:
                                alignment.append(AlignLabels.deletion)
                                ref_aligned.append(word)
                                hyp_aligned.append('')
                            ref_syllable_count = 0
                            
                            # Commit the alignment.
                            full_reference.extend(ref_aligned)
                            full_hypothesis.extend(hyp_aligned)
                            full_alignment.extend(alignment)
                            full_phone_align.append(phone_align.subsequence(0, i, preserve_index=False))
                            
                            # Add the remainder to the worklist
                            ref_word_span_next = (ref_word_index + len(ref_word_builder), ref_word_limit)
                            hyp_word_span_next = (hyp_word_index + len(hyp_word_builder), hyp_word_limit)
                            lev = Levenshtein.align(
                                ref=[x for x in phone_align.s1[i:] if x],
                                hyp=[x for x in phone_align.s2 if x],
                                reserve_list=PowerAligner.reserve_list, 
                                exclusive_sets=PowerAligner.exclusive_sets,
                                weights=Levenshtein.wordAlignWeights) #, 
                                #dist_penalty=PowerAligner.phoneDistPenalty, dist_penalty_set=Levenshtein.wordAlignWeights)
                            phone_align_next = lev.expandAlignCompact()
                            
                            worklist.append((ref_word_span_next, hyp_word_span_next, phone_align_next))
                            break					
                    elif ref_type == TokType.Phoneme and not ref_word_started:
                        ref_word_started = True
                        try:
                            ref_word_item = ref_word_iter.__next__()
                            ref_word_builder.append(ref_word_item[1])
                        except StopIteration:
                            pass
                    
                    if hyp_type == TokType.WordBoundary:
                        hyp_word_started = False
                        if ref_type != TokType.WordBoundary and hyp_word_builder and not ref_word_builder:
                            # INSERTION
                            # Hyp word ended, but no ref words have been added. Mark the current hyp word(s) in the span as insertion errors.
                            # TODO: Dedupe this logic
                            for word in hyp_word_builder:
                                alignment.append(AlignLabels.insertion)
                                ref_aligned.append('')
                                hyp_aligned.append(word)
                            hyp_syllable_count = 0
                            
                            # Commit the alignment.
                            full_reference.extend(ref_aligned)
                            full_hypothesis.extend(hyp_aligned)
                            full_alignment.extend(alignment)
                            full_phone_align.append(phone_align.subsequence(0, i, preserve_index=False))
                            
                            # Add the remainder to the worklist
                            ref_word_span_next = (ref_word_index + len(ref_word_builder), ref_word_limit)
                            hyp_word_span_next = (hyp_word_index + len(hyp_word_builder), hyp_word_limit)
                            lev = Levenshtein.align(
                                ref=[x for x in phone_align.s1 if x],
                                hyp=[x for x in phone_align.s2[i:] if x],
                                reserve_list=PowerAligner.reserve_list, 
                                exclusive_sets=PowerAligner.exclusive_sets,
                                weights=Levenshtein.wordAlignWeights) #, 
                                #dist_penalty=PowerAligner.phoneDistPenalty, dist_penalty_set=Levenshtein.wordAlignWeights)
                            phone_align_next = lev.expandAlignCompact()
                            
                            worklist.append((ref_word_span_next, hyp_word_span_next, phone_align_next))
                            break
                    elif hyp_type == TokType.Phoneme and not hyp_word_started:
                        hyp_word_started = True
                        try:
                            hyp_word_item = hyp_word_iter.__next__()
                            hyp_word_builder.append(hyp_word_item[1])
                        except StopIteration: 
                            pass
                        
                # Check for syllable mismatches
                if ref_type == TokType.SyllableBoundary:
                    ref_syllable_count += 1
                if hyp_type == TokType.SyllableBoundary:
                    hyp_syllable_count += 1
                    
                if (ref_type == TokType.SyllableBoundary == hyp_type or ref_syllable_count == hyp_syllable_count):
                    # No syllable conflicts here!
                    ref_extra_syllable_word_index = None
                    hyp_extra_syllable_word_index = None
                elif (ref_type == TokType.SyllableBoundary and 
                            not ref_extra_syllable_word_index and 
                            TokType.checkAnnotation(phone_align.s2[i - 1]) == TokType.WordBoundary):
                    # Extra syllable in hypothesis. We only care if the syllable immediately follows a word boundary. 
                    # This is because this indicates that a new word is being formed, which may likely be an insertion in hyp.
                    ref_extra_syllable_word_index = len(ref_word_builder) - 1
                    # print ref_word_builder
                    # print 'Syllable/word mismatch at', i
                    # print 'Extra hyp word:', ref_word_builder[ref_extra_syllable_word_index]
                elif (hyp_type == TokType.SyllableBoundary and 
                            not hyp_extra_syllable_word_index and 
                            TokType.checkAnnotation(phone_align.s2[i - 1]) == TokType.WordBoundary):
                    # This time there's an extra syllable in the ref, corresponding to a new ref word.
                    hyp_extra_syllable_word_index = len(hyp_word_builder) - 1
                    # print hyp_word_builder
                    # print 'Syllable/word mismatch at', i
                    # print 'Extra ref word:', hyp_word_builder[hyp_extra_syllable_word_index]
        # Concatenate all phoneme alignments
        fp_align = full_phone_align[0]
        for expand_align in full_phone_align[1:]:
            fp_align.append_alignment(expand_align)
            
        return ExpandedAlignment(full_reference, full_hypothesis, full_alignment), fp_align
            
