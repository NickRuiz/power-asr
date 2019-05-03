from power.levenshtein import ExpandedAlignment, AlignLabels
from power.aligner import CharToWordAligner
import re
import copy

class PunctInsertOracle(object):
    '''
    Insert punctuation on hypothesis based on alignment with reference
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def insertPunct(error_alignment, ref_punct):
        if not (error_alignment.s1_map and error_alignment.s2_map):
            # Don't try to add punct if either the hyp or ref are empty.
            return error_alignment
        
        # Align reference with punct against reference without punct
        # Is this needed? Yes, in case there's punctuation that makes an extra token
        ref_punct_tokens = ref_punct.split()
        ref_nopunct_tokens = error_alignment.s1_string().split() # [x for x in error_alignment.s1 if x]
        hyp_nopunct_tokens = error_alignment.s2_string().split() # [x for x in error_alignment.s2 if x]
        
        ref_punct_string = ' '.join(ref_punct_tokens)
        ref_nopunct_string = ' '.join(ref_nopunct_tokens)
        c2w_aligner = CharToWordAligner(ref_punct_string, ref_nopunct_string, lowercase=True)
        c2w_aligner.charAlign()
        ref_punct_align = c2w_aligner.charAlignToWordAlign()
        
#         lev = Levenshtein.align(ref_punct_tokens, ref_nopunct_tokens, lowercase=True)
#         lev.editops()
#         ref_punct_align = lev.expandAlign()
        
        error_alignment_punct = copy.deepcopy(error_alignment)
        
        try:
            err_align_index = None
            err_align_label = None
            ref_punct_index = -1
            ref_nopunct_index = -1
            for ref_align_index in range(len(ref_punct_align.align)):
                # Check the error type.
                ref_align_error_type = ref_punct_align.align[ref_align_index]
                ref_word_punct = ref_punct_align.s1[ref_align_index]
                ref_word_nopunct = ref_punct_align.s2[ref_align_index]
                
                punct_lhs = ""
                punct_rhs = ""
                                   
                if ref_align_error_type in (AlignLabels.correct, AlignLabels.substitution):
                    # There's some punct attached to the word. Split it off!
                    # Idea #1, Use regex to find punct around a word sequence. However, this will fail if there's punctuation in between words
                    pattern = '^(.*?){0}(.*?)$'.format(ref_word_nopunct)
                    match = re.search(pattern, ref_word_punct)
                    
                    if not match:
                        # Whoops! something went wrong
                        raise Exception("Regex match not found\nPattern: {0}\nPunct:    {1}\nNo Punct: {2}"
                                        .format(pattern, ref_word_nopunct, ref_word_nopunct))
                    punct_lhs = match.group(1)
                    punct_rhs = match.group(2)
                    
                    if punct_lhs:
                        # Apply to front of hyp
                        punct_lhs = punct_lhs.strip() 
                    else:
                        punct_lhs = ""
                    if punct_rhs:
                        # Apply to back of hyp
                        punct_rhs = punct_rhs.strip()
                    else:
                        punct_rhs = ""
                        
                    ref_punct_index += 1
                    ref_nopunct_index += 1
                        
                elif ref_align_error_type == AlignLabels.deletion:
                    # TODO: The extra token on the reference side is probably punct. Check if token is punct
                    # Determine if punct should attach as punct_lhs or punct_rhs. We'll make that decision later.
                    punct_lhs = '{0} '.format(ref_word_punct)
                    punct_rhs = ' {0}'.format(ref_word_punct)
                    
                    ref_punct_index += 1
                elif ref_align_error_type == 'I':
                    # TODO: uh-oh. This shouldn't happen!
                    ref_nopunct_index += 1
                    raise TypeError("Insertion errors shouldn't happen between punct and nopunct")
                else:
                    # Now this is impossible!
                    raise TypeError("Invalid error type: {0}".format(ref_align_error_type))
                
                # Advance error_alignment to the word alignment position containing the nopunct reference word
                if ref_nopunct_index >= 0: # TODO: Check if the words have changed.
                    try:
                        err_align_index = error_alignment.s1_map[ref_nopunct_index]
                        err_align_label = error_alignment_punct.align[err_align_index]
                    except Exception:
                        print(error_alignment)
                        print("ref_nopunct_index:", ref_nopunct_index)
                        print("ref_align_index:  ", ref_align_index)
                        raise
                        
                if punct_lhs or punct_rhs:
#                     print "Punct: |_{0}_| |_{1}_|".format(punct_lhs, punct_rhs)
                    if err_align_label == AlignLabels.deletion:
                        # If there's no token here, apply punct to previous or next
                        # TODO: This won't work for long strings of D's. You'll need to find the next closest one.
                        
                        # Scan backward for the previous non-empty hyp word. Try to apply the punct there.
                        err_align_index_shift = err_align_index - 1
                        
                        # ... except if the punct was at the end of the last ref word 
                        if ref_nopunct_index == len(ref_nopunct_tokens) - 1:
                            err_align_index_shift = error_alignment.s2_map[len(hyp_nopunct_tokens) - 1]
                            
                        while err_align_index_shift > 0 and not error_alignment.s2[err_align_index_shift]:
                            err_align_index_shift -= 1
                        if err_align_index_shift >= 0:
                            
                            # Apply punct to previous position
                            if ref_align_error_type == AlignLabels.deletion:
                                punct_lhs = ""
                                
                            error_alignment_punct.s2[err_align_index_shift] = "{1}{0}{2}".format(error_alignment_punct.s2[err_align_index_shift], punct_lhs, punct_rhs)
                        else:
                            # Scan forward for the next non-empty hyp word. Try to apply the punct there.
                            err_align_index_shift = err_align_index + 1
                            while err_align_index_shift < len(hyp_nopunct_tokens) and not error_alignment_punct.s2[err_align_index_shift]:
                                err_align_index_shift += 1
                            if err_align_index_shift < len(hyp_nopunct_tokens):
                                
                                # Apply punct to next position
                                if ref_align_error_type == "D":
                                    punct_rhs = ""
                                    
                                error_alignment_punct.s2[err_align_index_shift] = "{1}{0}{2}".format(error_alignment_punct.s2[err_align_index_shift], punct_lhs, punct_rhs)
                            else:
                                # Otherwise ignore punct altogether
                                print("Discarding punct")
                    else:
                        # Apply punct on the end of the current word.
                        if ref_align_error_type == "D":
                            punct_lhs = ""  # TODO: Is this assumption correct? Apply punct to rhs?
                            
                        # Force punct at the end of the last reference word to appear at the end of the hyp word
                        if ref_nopunct_index == len(ref_nopunct_tokens) - 1:
                            err_align_index_shift = error_alignment.s2_map[len(hyp_nopunct_tokens) - 1]
                            error_alignment_punct.s2[err_align_index_shift] = "{0}{1}".format(error_alignment_punct.s2[err_align_index_shift], punct_rhs)
                            punct_rhs = ""
                            
                        error_alignment_punct.s2[err_align_index] = "{1}{0}{2}".format(error_alignment_punct.s2[err_align_index], punct_lhs, punct_rhs)

        except Exception as e:
            # TODO: Add exception handling to output the sentences as well as the offending segment.
            raise
        
        return error_alignment_punct
        
            