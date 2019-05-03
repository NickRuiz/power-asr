from power.levenshtein import Levenshtein, ExpandedAlignment
from power.aligner import PowerAligner
import unittest

class LevenshteinPhones_Test(unittest.TestCase):

    def test_lev_phones1(self):
        ref =   [ "",  "",  "",   "",   "|", "#", "b", "uh", "ch", "#", "",   "er","#", "ih", "ng", "|" ]
        hyp =   [ "|", "#", "dh", "ax", "|", "#", "m", "ax", "ch", "#", "uh", "r", "#", "ih", "ng", "|" ]
        align = [ 'I', 'I', 'I',  'I',  'C', 'C', 'S', 'S',  'C',  'C', 'I',  'S', 'C', 'C',  'C',  'C' ]
        refwords = [x for x in ref if x]
        hypwords = [x for x in hyp if x]
        lev = Levenshtein.align(refwords, hypwords, lowercase=True,
                                weights=Levenshtein.wordAlignWeights,
                                reserve_list=PowerAligner.reserve_list, exclusive_sets=PowerAligner.exclusive_sets
                          )
        lev.editops()
        expand_align = lev.expandAlign()
        print(expand_align)
        self.assertEqual(expand_align.align, align)
        
    def test_fbk_u19(self):
        ref     = """|  #  ow  k  #  ey  |  #  ay  m  |  #  g  ow  #  ih  ng  |  #  t  ax  |  #  d  uw  |  #  ax  n  #  ah  dh  #  er  |  #  k  ah  t  |""".split()
        hyp     = """|  #      k                                                                              ae  n                    |                """.split()
        align   = """C  C  D   C  D  D   D  D  D   D  D  D  D  D   D  D   D   D  D  D  D   D  D  D  D   D  D  S   C  D  D   D   D  D   C  D  D  D   D  D""".split()
        lev = Levenshtein.align(ref, hyp, lowercase=True,
                                weights=Levenshtein.wordAlignWeights,
                                reserve_list=PowerAligner.reserve_list, exclusive_sets=PowerAligner.exclusive_sets
                                )
        expand_align = lev.expandAlignCompact()
        print(expand_align)
        print(' '.join(expand_align.align))
        print(' '.join(align))
        self.assertEqual(expand_align.align, align)
        
    def test_fbk_u58(self):
        ref     = """|  #  p   iy                  |""".split()
        hyp     = """|  #  hh  iy  |  #  s  eh  d  |""".split()
        align   = """C  C  S   C   I  I  I  I   I  C""".split()
        correct = """C  C  S   C   C  I  I  I   I  I""".split()
        lev = Levenshtein.align(ref, hyp, lowercase=True,
                                weights=Levenshtein.wordAlignWeights,
                                reserve_list=PowerAligner.reserve_list, exclusive_sets=PowerAligner.exclusive_sets
                                )
        expand_align = lev.expandAlignCompact()
        print(expand_align)
        self.assertEqual(expand_align.align, correct)
        
    def test_fbk_u268(self):
        # What the wrong alignment used to be.
        ref     = """|  #  ao  l  |  #  ae  t  |""".split()
        hyp     = """|  #  ao               r  |""".split()
        align   = """C  C  C   D  D  D  D   S  C""".split()
        correct = """C  C  C   S  C  D  D   D  D""".split()
        refwords = [x for x in ref if x]
        hypwords = [x for x in hyp if x]
        lev = Levenshtein.align(refwords, hypwords, lowercase=True,
                                weights=Levenshtein.wordAlignWeights,
                                reserve_list=PowerAligner.reserve_list, exclusive_sets=PowerAligner.exclusive_sets
                                )
        expand_align = lev.expandAlignCompact()
        print(expand_align)
        self.assertEqual(expand_align.align, correct)
        
    def test_fbk_u264_a(self):
        ref   = """So  the other elephant""".split()
        hyp   = """set in  _    an""".split()
        align = """S   S   D    S""".split()
        
        ref_phones     =  """|  #  s  ow  |  #  dh  ax  |  #  ah  dh  #  er  |  #  eh  l  #  ax  f  #  ax  n  t  |""".split()
        hyp_phones     =  """|  #  s  eh        t       |  #  ih  n          |                      #  ae  n  d  |""".split()
        align_phones   =  """C  C  C  S   D  D  S   D   C  C  S   S   D  D   C  D  D   D  D  D   D  C  S   C  S  C""".split()
        correct_phones =  """C  C  C  S   D  D  S   D   C  C  S   S   D  D   C  D  D   D  D  D   D  C  S   C  S  C""".split()
        
        
        refwords = ' '.join([r for r in ref if r != '_'])
        hypwords = ' '.join([h for h in hyp if h != "_"])
        
        lev = Levenshtein.align(ref_phones, hyp_phones, 
                  PowerAligner.reserve_list, PowerAligner.exclusive_sets, 
                  weights=Levenshtein.wordAlignWeights)
        #expand_align = lev.expandAlignCompact()
        lev.editops()
        expand_align = lev.expandAlign()
        
        print(expand_align)
        self.assertEqual(expand_align.align, correct_phones)
        
    def test_fbk_u264_b_1(self):
        # What the wrong alignment used to be.
        ref     = """|  #  k  l  ih  r  |  #  t  ax  |""".split()
        hyp     = """|  #     f  ih           t      |""".split()
        align   = """C  C  D  S  C   D  D  D  C  D   C""".split()
        correct = """C  C  D  S  C   D  D  D  C  D   C""".split()
        refwords = [x for x in ref if x]
        hypwords = [x for x in hyp if x]
        lev = Levenshtein.align(refwords, hypwords, lowercase=True,
                                weights=Levenshtein.wordAlignWeights,
                                reserve_list=PowerAligner.reserve_list, exclusive_sets=PowerAligner.exclusive_sets
                                )
        expand_align = lev.expandAlignCompact()
        print(expand_align)
        self.assertEqual(expand_align.align, correct)
            
    def test_fbk_u264_b_2(self):
        # What the wrong alignment used to be.
        ref     = """|  #     ao  l  |  #  ah  v  |""".split()
        hyp     = """|  #  f  ao               r  |""".split()
        align   = """C  C  I  C   D  D  D  D   S  C""".split()
        correct = """C  C  I  C   S  C  D  D   D  D""".split()
        refwords = [x for x in ref if x]
        hypwords = [x for x in hyp if x]
        lev = Levenshtein.align(refwords, hypwords, lowercase=True,
                                weights=Levenshtein.wordAlignWeights,
                                reserve_list=PowerAligner.reserve_list, exclusive_sets=PowerAligner.exclusive_sets
                                )
        expand_align = lev.expandAlignCompact()
        print(expand_align)
        self.assertEqual(expand_align.align, correct)
                                
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()