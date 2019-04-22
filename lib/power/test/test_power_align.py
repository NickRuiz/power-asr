from lib.power.aligner import PowerAligner
from lib.power.levenshtein import ExpandedAlignment
import unittest

class PowerAlign_test(unittest.TestCase):

    def test_fbk_u264_a(self):
        ref   = ["So the", "other", "elephant"]
        hyp   = """set      in       an""".split()
        align = """S        S        S""".split()
        
        ref_phones     =  """|  #  s  ow  |  #  dh  ax  |  #  ah  dh  #  er  |  #  eh  l  #  ax  f  #  ax  n  t  |""".split()
        hyp_phones     =  """|  #  s  eh        t       |  #  ih  n          |                      #  ae  n  d  |""".split()
        align_phones   =  """C  C  C  S   D  D  S   D   C  C  S   S   D  D   C  D  D   D  D  D   D  C  S   C  S  C""".split()
        correct_phones =  """C  C  C  S   D  D  S   D   C  C  S   S   D  D   C  C  D   D  D  D   D  D  S   C  S  C""".split()
        
        
        refwords = ' '.join([r for r in ref if r != '_'])
        hypwords = ' '.join([h for h in hyp if h != "_"])
        
        word_align, phone_align = PowerAligner.phoneAlignToWordAlign(refwords.split(), hypwords.split(), ref_phones, hyp_phones)
        print(word_align)
        print(phone_align)
        self.assertEqual(word_align.align, align)
        self.assertEqual(word_align.s1, [x if x != "_" else "" for x in ref])
        self.assertEqual(word_align.s2, [x if x != "_" else "" for x in hyp])
        
    def test_fbk_u264_b(self):
        ref   = ["clear to",  "all", "of",  "you"]
        hyp   = """fit      for _   the""".split()
        align = """S        S   D   S """.split()
        
        ref_phones     =  """|  #  k  l  ih  r  |  #  t  ax  |  #     ao  l  |  #  ah  v  |  #  y   uw  |""".split()
        hyp_phones     =  """|  #     f  ih           t      |  #  f  ao               r  |  #  dh  ax  |""".split()
        align_phones   =  """C  C  D  S  C   D  D  D  C  D   C  C  I  C   D  D  D  D   S  C  C  S   S   C""".split()
        correct_phones =  """C  C  D  S  C   D  D  D  C  D   C  C  I  C   S  D  D  D   D  C  C  S   S   C""".split()
        
        
        refwords = ' '.join([r for r in ref if r != '_'])
        hypwords = ' '.join([h for h in hyp if h != "_"])
        
        word_align, phone_align = PowerAligner.phoneAlignToWordAlign(refwords.split(), hypwords.split(), ref_phones, hyp_phones)
        print(word_align)
        print(phone_align)
        self.assertEqual(word_align.align, align)
        self.assertEqual(word_align.s1, [x if x != "_" else "" for x in ref])
        self.assertEqual(word_align.s2, [x if x != "_" else "" for x in hyp])
        
    def test_fbk_u268(self):
        ref =   """all at""".split()
        hyp =   """or  _""".split()
        align = """S   D""".split()
        
        refwords = ' '.join([r for r in ref if r != '_'])
        hypwords = ' '.join([h for h in hyp if h != "_"])
        
        # What the wrong alignment used to be.
        ref_phones     = """|  #  ao  l  |  #  ae  t  |""".split()
        hyp_phones     = """|  #  ao               r  |""".split()
        align_phones   = """C  C  C   D  D  D  D   S  C""".split()
        correct_phones = """C  C  C   S  C  D  D   D  D""".split()
        
        word_align, phone_align = PowerAligner.phoneAlignToWordAlign(refwords.split(), hypwords.split(), ref_phones, hyp_phones)
        print(word_align)
        print(phone_align)
        self.assertEqual(word_align.align, align)
        self.assertEqual(word_align.s1, [x if x != "_" else "" for x in ref])
        self.assertEqual(word_align.s2, [x if x != "_" else "" for x in hyp])
        
    def test_fbk_u198_b(self):
        ref   = """and is going to pull it  in""".split()
        hyp   = """an   _  _     _  _   _  end""".split()
        align = """S   D  D     D  D    D   S""".split()
        
        ref_phones     =  """|  #  ae  n  d  |  #  ih  z  |  #  g  ow  #  ih  ng  |  #  t  ax  |  #  p  uh  l  |  #  ih  t  |  #  ih  n     |""".split()
        hyp_phones     =  """                                                                                  |  #  ae  n  |  #  eh  n  d  |""".split()
        align_phones   =  """D  D  D   D  D  D  D  D   D  D  D  D  D   D  D   D   D  D  D  D   D  D  D  D   D  C  C  S   S  C  C  S   C  I  C""".split()
        correct_phones =  """C  C  C   C  D  D  D  D   D  D  D  D  D   D  D   D   D  D  D  D   D  D  D  D   D  D  D  D   D  C  C  S   C  I  C""".split()
        
        
        refwords = ' '.join([r for r in ref if r != '_'])
        hypwords = ' '.join([h for h in hyp if h != "_"])
        
        word_align, phone_align = PowerAligner.phoneAlignToWordAlign(refwords.split(), hypwords.split(), ref_phones, hyp_phones)
        print(word_align)
        print(phone_align)
        self.assertEqual(word_align.align, align)
        self.assertEqual(word_align.s1, [x if x != "_" else "" for x in ref])
        self.assertEqual(word_align.s2, [x if x != "_" else "" for x in hyp])
        
    def test_kit_u264_a(self):
        ref   = """aortic  _   root   graft""".split()
        hyp   = """able    to  group  graph""".split()
        align = """S       I   S      S""".split()
        
        ref_phones     =  """|  #  ao  r  t  #  ih  k  |  #                  r  uw  t  |  #  g  r  ae  f  t |""".split()
        hyp_phones     =  """|  #  ey  b     #  ax  l  |  #  t  ax  |  #  g  r  uw  p  |  #  g  r  ae  f    |""".split()
        align_phones   =  """C  C  S   S  D  C  S   S  C  C  I  I   I  I  I  C  C   S  C  C  C  C  C   C  D C""".split()
        correct_phones =  """C  C  S   S  D  C  S   S  C  C  I  I   I  I  I  C  C   S  C  C  C  C  C   C  D C""".split()
        
        
        refwords = ' '.join([r for r in ref if r != '_'])
        hypwords = ' '.join([h for h in hyp if h != "_"])
        
        word_align, phone_align = PowerAligner.phoneAlignToWordAlign(refwords.split(), hypwords.split(), ref_phones, hyp_phones)
        print(word_align)
        print(phone_align)
        self.assertEqual(word_align.align, align)
        self.assertEqual(word_align.s1, [x if x != "_" else "" for x in ref])
        self.assertEqual(word_align.s2, [x if x != "_" else "" for x in hyp])

if __name__ == "__main__":
    unittest.main()