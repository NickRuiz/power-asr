from normalize import NumToTextEng, TextToNumEng
from normalize import ContractionsEng
from power.levenshtein import ExpandedAlignment
import re
from collections import defaultdict
import itertools
import string

def splitHyphens(text):
    return [x for x in re.split('[ -]', text) if x]

class HypothesisNormalizer(object):
    '''
    Normalizes a hypothesis towards a reference.
    Currently numbers, hyphens, and contractions are implemented (reduce and expand).
    '''
    
    @staticmethod
    def normalizeAligned(expand_align, fix_casing=False):
        # Given a Levenshtein-aligned utterance pair, normalize the aligned hypothesis to look like the reference.

        # Pass #1, only fix substitution errors
        for i in range(expand_align.length()):
            if expand_align.align[i] == 'S':
                expand_align.s2[i] = HypothesisNormalizer.normalize(expand_align.s2[i], expand_align.s1[i])
                
                if ' '.join(expand_align.s2[i]).lower() == ' '.join(expand_align.s1[i]).lower():
                    expand_align.align[i] = 'C'
                    
            if expand_align.align[i] == 'C' and fix_casing:
                expand_align.s2[i] = expand_align.s1[i]
        normed_components = expand_align.s2
            
        # Pass #2, find error regions and correct them.
        split_regions, error_indexes = expand_align.split_error_regions()
        if len(error_indexes) > 0:
            normed_components = []
            for i in range(len(split_regions)):
                if i not in error_indexes:
                    normed_components.append(split_regions[i].s2_string())
                else:
                    seg = split_regions[i]
                    normed = HypothesisNormalizer.normalize(seg.s2_string(), seg.s1_string())
                    normed_components.append(normed)
        
        return ' '.join(normed_components)
    
    @staticmethod
    def normalize(hyp, ref):
        # Normalizes the hypothesis toward the reference (no alignment required).
        hyp_fixed = ' '.join(HypothesisNormalizer.normalizeHyphenated(hyp, ref, removeHyphens=True))
        if hyp_fixed != ref:
            hyp_fixed = ' '.join(HypothesisNormalizer.normalizeHyphenated(hyp_fixed, ref, removeHyphens=False))
        return hyp_fixed
        
    @staticmethod
    def normalizeHyphenated(hyp, ref, removeHyphens=False):
        if removeHyphens:   
            refwords = splitHyphens(ref)
            hypwords = splitHyphens(hyp)
        else:
            refwords = ref.split()
            hypwords = hyp.split()
             
        hyp_start = 0
        ref_start = 0
        
        hyp_normalized = list()
        
        while (hyp_start < len(hypwords)):
            # Find the first hyp word that may need correcting.
            while (hyp_start < len(hypwords) and
                   ref_start < len(refwords) and
                    (hypwords[hyp_start].lower() == refwords[ref_start].lower())):
                hyp_normalized.append(hypwords[hyp_start])
                hyp_start += 1
                ref_start += 1
            if hyp_start < len(hypwords):
                if ref_start >= len(refwords):
                    hyp_normalized.append(hypwords[hyp_start])
                    hyp_start += 1
                    continue
                
                # There's a hyp word that doesn't match the ref word. Try to fix it.
                ref_span_str = ' '.join(refwords[ref_start:])
                
                hyp_match_string = None
                best_ref_index_end = None
                hyp_stop_index = -1
                rollback_dist = 0
                
                for hyp_span, hyp_stop_index in HypothesisNormalizer.wordSpans(hypwords, hyp_start, len(hypwords)):
                    # Convert the word span into a string
                    hyp_span_str = ' '.join(hyp_span)
                    # Find the normalization options for the current span
                    # TODO: no 'th' suffixes right now
                    norm_options = HypothesisNormalizer.getNormOptions(hyp_span_str)
                    norm_options['text'].add(hyp_span_str)
                    # norm_options = defaultdict(set)
                    # norm_options.keys() = ['text', 'num', 'textnum', 'textyear']
                    
                    # Collapse the options
                    # sort by number of words (descending)
                    norm_options_collapsed = [re.escape(x) for x in 
                                              sorted(
                                                    sorted(set(itertools.chain(*norm_options.values())), 
                                                           key=lambda x: -len(x)),
                                                    key=lambda x: -len(x.split()))]
                    
                    # Look for matches (or near matches)
                    match = re.search("(^| )({0})".format("|".join(norm_options_collapsed)), ref_span_str, re.IGNORECASE)
                    rollback_dist += 1
                    
                    # The first match should be the best match.
                    if not match:
                        # If there's a number option, try continuing to see if it can be resolved.
                        # TODO: This could lead to some problems.
                        if 'num' in norm_options:
                            # Check if the numbers have zeroes at the end.
                            zero_term_nums = [re.escape(x.rstrip('0')) for x in norm_options['num'] if len(x) > 1 and x[-1] == '0']
                            # Check for a partial match
                            if zero_term_nums and re.search("(^| )({0})".format("|".join(zero_term_nums)), ref_span_str, re.IGNORECASE):
                                continue
                        # Abandon the current hyp and move on
                        break
                    
                    # Check if the word was completed.
                    best_ref_index_end = match.regs[2][1]
                    match_string = match.group(2)
                    
                    if len(ref_span_str) == best_ref_index_end or ref_span_str[best_ref_index_end] == ' 'in set([' ', '-']):
                        # Full match. Store this intermediate string as a possible normalization match
                        hyp_match_string = match_string
                        rollback_dist = 0
                
                # Check if a match was found.
                if hyp_match_string:
                    hyp_normalized.append(hyp_match_string)
                    hyp_start = hyp_stop_index - rollback_dist
                    ref_start = len(ref_span_str[:best_ref_index_end].split(" "))
                else:
                    hyp_normalized.append(hypwords[hyp_start])
                hyp_start += 1
                
        return hyp_normalized
    
    @staticmethod
    def wordSpans(hyp_words, start_index, end_index = -1):
        '''
        Generates all subsequences of words always starting at start_index.
        '''
        if end_index < 0:
            end_index = len(hyp_words)
        for stop_index in range(start_index, end_index):
            yield hyp_words[start_index:stop_index+1], stop_index
    
    @staticmethod
    def normalizeHyphens(hyp, ref):
        '''
        Greedy algorithm. Potentially suboptimal.
        '''
        if not hyp:
            return ""
        if not ref:
            return hyp
        
        hyp_words = hyp.replace('-', ' ').split()
        if hyp[0] == '-':
            hyp_words[0] = '-{0}'.format(hyp_words[0])
        if hyp[-1] == '-':
            hyp_words[-1] = '{0}-'.format(hyp_words[-1])
            
        hyp_word_start = 0
        hyp_word_end = 0
        ref_index = 0
        best_ref_index = 0
        
        hyp_fixed = []
        hyp_match_string = None
        
        end_compare = False
        while hyp_word_start < len(hyp_words):
            if hyp_word_end == len(hyp_words) - 1:
                end_compare = True
            
            if hyp_word_start < len(hyp_words) - 1:
                # Span from hyp_word_start to hyp_word_end 
                hyp_span = hyp_words[hyp_word_start:hyp_word_end+1]
                hyp_options = '[ \-]'.join(hyp_span)
                
                #print "Pattern:", hyp_options
                
                match = re.search("({0})".format(hyp_options), ref[ref_index:], re.IGNORECASE)
                if match:
                    best_ref_index = match.regs[1][1]
                    hyp_match_string = match.group(1)
                    hyp_word_end += 1
                else:
                    end_compare = True
            else:
                end_compare = True
                    
            if end_compare:
                # Roll back to previous best
                if hyp_match_string:
                    # Add it to the output
                    hyp_fixed.append(hyp_match_string)
                    ref_index = best_ref_index
                else:
                    # Add whatever junk was at hyp_word_start
                    hyp_word_end = hyp_word_start + 1
                    hyp_fixed.append(hyp_words[hyp_word_start])
                     
                #print hyp_word_end, "Current:", hyp_fixed
                hyp_word_start = hyp_word_end
                hyp_match_string = None
                end_compare = False
            
        return ' '.join(hyp_fixed)
                      
    @staticmethod
    def isDashEquivalent(hyp, ref):
        # Dashes must be between words
        if '-' in (hyp[0], hyp[-1], ref[0], ref[-1]):
            return False
        
        # Strip the dashes, then compare tokens
        hyp_words = hyp.replace('-', ' ').split()
        ref_words = ref.replace('-', ' ').split()
        return (hyp_words == ref_words)
        
    @staticmethod
    def getNormOptions(word_string, extended=True):
        # Returns possible ways to normalize the string
        options_dict = defaultdict(set)
        
        # Number conversion
        if word_string.isdigit():
            word_number = int(word_string)
            # Convert digits to words
            try:
                num_text = NumToTextEng.convert(word_number)
                options_dict['textnum'].add(num_text)
            except:
                pass
            
            # Convert digits to year
            try:
                num_text = NumToTextEng.convertTryYear(word_number)
                options_dict['textyear'].add(num_text)
            except:
                pass
        else:
            if extended and len(word_string.split()) > 1:
                ext = set()

                # Hyphenation
                ext.add('-'.join(word_string.split()))
                
                # All one single word
                ext.add(''.join(word_string.split()))

                # Strip punctuation (both sides)
                ext.add(word_string.strip(string.punctuation))
                # Strip left punct only
                ext.add(word_string.lstrip(string.punctuation))
                # Strip right punct only
                ext.add(word_string.rstrip(string.punctuation))
                options_dict['extended'].update(ext)

            
            wstr = word_string
            # Deyphenation 
            if '-' in word_string:
                wstr = word_string.replace('-', ' ')
                options_dict['text'].add(wstr)
            
            # Convert words to digits
            try:                    
                num = TextToNumEng.convertTryYear(wstr)
                options_dict['num'].add(str(num))
            except:
                pass

            # Contractions
            if "'" in word_string:
                # Expand contractions
                cont_options = ContractionsEng.expandOptions(word_string)
            else:
                # Apply contractions 
                cont_options = ContractionsEng.contractOptions(word_string)
            if cont_options:
                options_dict['text'].update(cont_options)
                
        return options_dict
