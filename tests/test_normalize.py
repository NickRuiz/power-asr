import unittest
from normalize import HypothesisNormalizer
from power.levenshtein import ExpandedAlignment
import itertools

class NormalizeHyphens_Test(unittest.TestCase):
    def test_normalizeHyphens_true(self):
        hyp = "one two one life"
        ref = "one-to-one"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        expected = ref
        self.assertNotEqual(actual, expected)
        
    def test_normalizeHyphens_match_simple(self):
        hyp = "touch interactive"
        ref = "touch-interactive"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        
        expected = ref
        self.assertEqual(actual, expected)  
        
    def test_normalizeHyphens_notmatch_simple(self):
        hyp = "touch interactive"
        ref = "it's touch-interactive"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        
        expected = "touch-interactive"
        self.assertEqual(actual, expected)
        
    def test_normalizeHyphens_notmatch_simple_reverse(self):
        hyp = "it's touch-interactive"
        ref = "touch interactive"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        
        expected = "it's touch interactive"
        self.assertEqual(actual, expected)
        
    def test_isDashEquivalent_false_front(self):
        hyp = "-touch-interactive"
        ref = "touch-interactive"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        
        expected = "touch-interactive"
        self.assertEqual(actual, expected)
        
    def test_isDashEquivalent_false_back(self):
        hyp = "touch-interactive-"
        ref = "touch-interactive"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        
        expected = "touch-interactive"
        self.assertEqual(actual, expected)

class Normalize_Test(unittest.TestCase):
    def test_getNormOptions_number_2012(self):
        expected = set(['two thousand twelve', 'twenty twelve'])
        actual = HypothesisNormalizer.getNormOptions("2012")
        actual = set(itertools.chain(*actual.values()))
        self.assertEqual(actual, expected)
        
    def test_getNormOptions_text_124(self):
        actual = HypothesisNormalizer.getNormOptions("one hundred twenty-four", extended=False)
        expected = set(['one hundred twenty four', '124'])
        actual = set(itertools.chain(*actual.values()))
        self.assertEqual(actual, expected)
        
    def test_getNormOptions_contract_dont(self):
        actual = HypothesisNormalizer.getNormOptions("don't")
        actual = set(itertools.chain(*actual.values()))
        expected = set(['do not'])
        self.assertEqual(actual, expected)
        
    def test_getNormOptions_fifty(self):
        actual = HypothesisNormalizer.getNormOptions("fifty")
        actual = set(itertools.chain(*actual.values()))
        expected = set(['50'])
        self.assertEqual(actual, expected)
        
    def test_isDashEquivalent(self):
        hyp = "touch interactive"
        ref = "touch-interactive"
        actual = HypothesisNormalizer.isDashEquivalent(hyp, ref)
        self.assertTrue(actual)
        
    def test_isDashEquivalent_false_front(self):
        hyp = "-touch interactive"
        ref = "touch-interactive"
        actual = HypothesisNormalizer.isDashEquivalent(hyp, ref)
        self.assertFalse(actual)
        
    def test_isDashEquivalent_false_back(self):
        hyp = "touch interactive"
        ref = "touch-interactive-"
        actual = HypothesisNormalizer.isDashEquivalent(hyp, ref)
        self.assertFalse(actual)
        
    # Test normalize
    def test_normalize_digits_and_words(self):
        hyp = "234 thousand"
        ref = "two hundred thirty four thousand"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        
        self.assertEqual(actual, ref)
    
    def test_normalize_digits(self):
        hyp = "234000"
        ref = "two hundred thirty four thousand"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        
        self.assertEqual(actual, ref) 
        
    def test_normalize_words_identical(self):
        hyp = "two hundred thirty four thousand"
        ref = "two hundred thirty four thousand"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        
        self.assertEqual(actual, ref) 

    def test_normalize_words_hyphen(self):
        hyp = "two hundred thirty-four thousand"
        ref = "two hundred thirty four thousand"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        
        self.assertEqual(actual, ref) 
        
    def test_normalize_words_missing_back(self):
        hyp = "two hundred thirty four"
        ref = "two hundred thirty four thousand"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        
        self.assertEqual(actual, hyp)
        self.assertNotEqual(actual, ref) 
        
    def test_normalize_words_missing_front(self):
        hyp = "hundred thirty four thousand"
        ref = "two hundred thirty four thousand"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        
        self.assertEqual(actual, hyp)
        self.assertNotEqual(actual, ref)
        
    def test_normalize_fifty_year_old(self):
        hyp = "fifty year old"
        ref = "50 year old"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        
        self.assertEqual(actual, ref)
    
    def test_normalize_fifty_year_old_hyphen(self):
        # TODO: This one has a hyphenation issue that needs to be resolved.
        hyp = "fifty year old"
        ref = "fifty-year-old"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        
        self.assertEqual(actual, ref)
        
    def test_normalize_fifty_year_old_num_hyphen(self):
        # TODO: This one has a hyphenation issue that needs to be resolved.
        hyp = "fifty year old"
        ref = "50-year-old"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        
        self.assertEqual(actual, ref)
        
    def test_normalize_ref_extra_words(self):
        hyp = "the fifty year old"
        ref = "a 50 year old"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        
        expected = "the 50 year old"
        self.assertEqual(actual, expected)
        
    def test_normalize_middle_age(self):
        ref = "than middle-aged"
        hyp = "the middle age"
        expected = "the middle age"
        actual = HypothesisNormalizer.normalize(hyp, ref)
        self.assertEqual(actual, expected)
         
        
#     def test_normalize_911(self):
#         hyp = "nine 11"
#         ref = "911"
#         actual = HypothesisNormalizer.normalize(hyp, ref)
#         expected = "911"
#         self.assertEqual(actual, expected)

    def test_normalize_alignment_contraction(self):
        ref_aligned = [u'A', u'50-year-old', u'business', u'man', u'lamented', u'to', u'me', u'that', u'he', u'feels', u'he', u"doesn't", u'have', u'colleagues', u'anymore', u'at', u'work']
        hyp_aligned = [u'', u'fifty year old', u'business', u'man', u'laments', u'to', u'me', u'that', u'he', u'feels', u'he', u'does not', u'have', u'colleagues', u'any more', u'it', u'work']
        alignment = [u'D', u'S', u'C', u'C', u'S', u'C', u'C', u'C', u'C', u'C', u'C', u'S', u'C', u'C', u'S', u'S', u'S']
        expand_align = ExpandedAlignment(ref_aligned, hyp_aligned, alignment, lowercase=True) 
        actual = HypothesisNormalizer.normalizeAligned(expand_align)
        expected = ' '.join([u'', u'50-year-old', u'business', u'man', u'laments', u'to', u'me', u'that', u'he', u'feels', u'he', u"doesn't", u'have', u'colleagues', u'anymore', u'it', u'work'])
        self.assertEqual(actual, expected)
        
    def test_normalize_alignment_any_more(self):
        hyp_aligned = ["any more"]
        ref_aligned = ["anymore"]
        alignment = ["S"]
        expand_align = ExpandedAlignment(ref_aligned, hyp_aligned, alignment, lowercase=True) 
        actual = HypothesisNormalizer.normalizeAligned(expand_align)
        expected = ' '.join(ref_aligned)
        self.assertEqual(actual, expected)  
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
