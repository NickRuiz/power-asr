import unittest
from normalize import HypothesisNormalizer
from power.levenshtein import ExpandedAlignment

class NormalizeAlign_Test(unittest.TestCase):

    # normalizeAligned
    def test_normalizeAlignment_911(self):
        ref_aligned = [u'Everyone', u'who', u'knew', u'me', u'before', u'911',     u'',    u'believes', u"I'm", u'dead']
        hyp_aligned = [u'everyone', u'who', u'knew', u'me', u'before', u'nine 11', u'the', u'believes', u'line', u'']
        alignment = [u'C', u'C', u'C', u'C', u'C', u'S', u'I', u'S', u'S', u'D']
        expected = ' '.join([u'everyone', u'who', u'knew', u'me', u'before', u'911', u'the', u'believes', u'line', u'']).strip()
        expand_align = ExpandedAlignment(ref_aligned, hyp_aligned, alignment, lowercase=True)
        actual = HypothesisNormalizer.normalizeAligned(expand_align)
        self.assertEqual(actual, expected)
        
    def test_normalizeAlignment_textnum_hyphen(self):
        ref_aligned = [u'A', u'50-year-old', u'business', u'man', u'lamented', u'to', u'me', u'that', u'he', u'feels', u'he', u"doesn't", u'have', u'colleagues', u'anymore', u'at', u'work']
        hyp_aligned = [u'', u'fifty year old', u'business', u'man', u'laments', u'to', u'me', u'that', u'he', u'feels', u'he', u"doesn't", u'have', u'colleagues', u'anymore', u'it', u'work']
        alignment =  [u'D', u'S', u'C', u'C', u'S', u'C', u'C', u'C', u'C', u'C', u'C', u'C', u'C', u'C', u'C', u'S', u'C']
        expected = ' '.join([u'', u'50-year-old', u'business', u'man', u'laments', u'to', u'me', u'that', u'he', u'feels', u'he', u"doesn't", u'have', u'colleagues', u'anymore', u'it', u'work'])
        expand_align = ExpandedAlignment(ref_aligned, hyp_aligned, alignment, lowercase=True) 
        actual = HypothesisNormalizer.normalizeAligned(expand_align)
        self.assertEqual(actual, expected)
        
    def test_normalizeAlignment_text_hyphen(self):
        ref_aligned = [u'Our', u'digital', u'body', u'is', u'', u'', u'', u'', u'one-to-one', u'life']
        hyp_aligned = [u'are', u'what', u'it', u'is', u'all', u'about', u'the', u'these', u'one to one', u'life']
        alignment = [u'S', u'S', u'S', u'C', u'I', u'I', u'I', u'I', u'S', u'C']
        expected = ' '.join([u'are', u'what', u'it', u'is', u'all', u'about', u'the', u'these', u'one-to-one', u'life'])
        expand_align = ExpandedAlignment(ref_aligned, hyp_aligned, alignment, lowercase=True) 
        actual = HypothesisNormalizer.normalizeAligned(expand_align)
        self.assertEqual(actual, expected)
        
    def test_normalizeAlignment_number(self):
        ref_aligned = [u'You', u'need', u'to', u'know', u'that', u'the', u'average', u'patent', u'troll', u'defense', u'costs', u'two million', u'dollars', u'and', u'takes', u'18', u'months', u'when', u'you', u'win']
        hyp_aligned = [u'you', u'need', u'to', u'know', u'that', u'the', u'average', u'patent', u'troll', u'defense', u'cost', u'2000000', u'dollars', u'and', u'takes', u'18', u'months', u'when', u'you', u'win']
        alignment = [u'C', u'C', u'C', u'C', u'C', u'C', u'C', u'C', u'C', u'C', u'S', u'S', u'C', u'C', u'C', u'C', u'C', u'C', u'C', u'C']
        expected = ' '.join([u'you', u'need', u'to', u'know', u'that', u'the', u'average', u'patent', u'troll', u'defense', u'cost', u'two million', u'dollars', u'and', u'takes', u'18', u'months', u'when', u'you', u'win'])
        expand_align = ExpandedAlignment(ref_aligned, hyp_aligned, alignment, lowercase=True) 
        actual = HypothesisNormalizer.normalizeAligned(expand_align)
        self.assertEqual(actual, expected)
        
    def test_normalize_alignment_year(self):
        ref_aligned = ["Now",  "fast-forward",  "to",  "2012"]
        hyp_aligned = ["now",  "fast-forward",  "to",  "twenty twelve"]
        alignment   = ["C",    "C",             "C",   "S"]
        expected    = ' '.join(["now",  "fast-forward",  "to",  "2012"])
        expand_align = ExpandedAlignment(ref_aligned, hyp_aligned, alignment, lowercase=True) 
        actual = HypothesisNormalizer.normalizeAligned(expand_align)
        self.assertEqual(actual, expected)
        
    def test_normalize_alignment_theyre1(self):
        ref_aligned = [ "In",  "our",  "study",  "they",  "are",  "more",  "positive",  "but",  "they're",   "also",  "more",  "likely",  "than",  "younger",  "people",  "to",  "experience",  "mixed",  "emotions",  "sadness",  "at",  "the",  "same",  "time",  "you",  "experience",  "happiness",  "you",  "know",  "that",  "tear",  "in",  "the",  "eye",  "when",  "you're",  "smiling",  "at",  "a",  "friend" ]
        hyp_aligned = [ "in",  "our",  "study",  "they",  "are",  "more",  "positive",  "but",  "they are",  "also",  "more",  "likely",  "than",  "younger",  "people",  "to",  "experience",  "mixed",  "emotions",  "sadness",  "at",  "the",  "same",  "time",  "you",  "experience",  "happiness",  "you",  "know",  "that",  "tear",  "in",  "the",  "eye",  "when",  "you're",  "smiling",  "at",  "a",  "friend" ]
        alignment   = [ "C",   "C",    "C",      "C",     "C",    "C",     "C",         "C",    "S",         "C",     "C",     "C",       "C",     "C",        "C",       "C",   "C",           "C",      "C",         "C",        "C",   "C",    "C",     "C",     "C",    "C",           "C",          "C",    "C",     "C",     "C",     "C",   "C",    "C",    "C",     "C",       "C",        "C",   "C",  "C" ]   
        expected    = ' '.join([ "in",  "our",  "study",  "they",  "are",  "more",  "positive",  "but",  "they're",   "also",  "more",  "likely",  "than",  "younger",  "people",  "to",  "experience",  "mixed",  "emotions",  "sadness",  "at",  "the",  "same",  "time",  "you",  "experience",  "happiness",  "you",  "know",  "that",  "tear",  "in",  "the",  "eye",  "when",  "you're",  "smiling",  "at",  "a",  "friend" ])
        expand_align = ExpandedAlignment(ref_aligned, hyp_aligned, alignment, lowercase=True) 
        actual = HypothesisNormalizer.normalizeAligned(expand_align)
        self.assertEqual(actual, expected)
        
    def test_normalize_alignment_theyre2(self):
        ref_aligned = [ "In",  "our",  "study",  "they",  "are",  "more",  "positive",  "but",  "they're",  "",     "also",  "more",  "likely",  "than",  "younger",  "people",  "to",  "experience",  "mixed",  "emotions",  "sadness",  "at",  "the",  "same",  "time",  "you",  "experience",  "happiness",  "you",  "know",  "that",  "tear",  "in",  "the",  "eye",  "when",  "you're",  "smiling",  "at",  "a",  "friend" ]
        hyp_aligned = [ "in",  "our",  "study",  "they",  "are",  "more",  "positive",  "but",  "they",     "are",  "also",  "more",  "likely",  "than",  "younger",  "people",  "to",  "experience",  "mixed",  "emotions",  "sadness",  "at",  "the",  "same",  "time",  "you",  "experience",  "happiness",  "you",  "know",  "that",  "tear",  "in",  "the",  "eye",  "when",  "you're",  "smiling",  "at",  "a",  "friend" ]
        alignment   = [ "C",   "C",    "C",      "C",     "C",    "C",     "C",         "C",    "S",        "I",    "C",     "C",     "C",       "C",     "C",        "C",       "C",   "C",           "C",      "C",         "C",        "C",   "C",    "C",     "C",     "C",    "C",           "C",          "C",    "C",     "C",     "C",     "C",   "C",    "C",    "C",     "C",       "C",        "C",   "C",  "C" ]   
        expected    = ' '.join([ "in",  "our",  "study",  "they",  "are",  "more",  "positive",  "but",  "they're",          "also",  "more",  "likely",  "than",  "younger",  "people",  "to",  "experience",  "mixed",  "emotions",  "sadness",  "at",  "the",  "same",  "time",  "you",  "experience",  "happiness",  "you",  "know",  "that",  "tear",  "in",  "the",  "eye",  "when",  "you're",  "smiling",  "at",  "a",  "friend" ])
        expand_align = ExpandedAlignment(ref_aligned, hyp_aligned, alignment, lowercase=True) 
        actual = HypothesisNormalizer.normalizeAligned(expand_align)
        self.assertEqual(actual, expected)
        
    def test_normalize_alignment_ex1(self):
        ref_aligned = [  "Our",  "digital",   "body",  "is",  "one-to-one",  "",     "",      "life",  "size",  "so",  "this",  "is",  "exactly",  "the",  "way",  "students",  "will",   "see",  "the",  "real",  "anatomy", ]
        hyp_aligned = [  "our",  "peaceful",  "body",  "is",  "one two",     "one",  "life",  "life",  "size",  "so",  "this",  "is",  "exactly",  "the",  "way",  "students",  "would",  "see",  "the",  "real",  "anatomy", ]
        alignment   = [  "C",    "S",         "C",     "C",   "S",           "I",    "I",     "C",     "C",     "C",   "C",     "C",   "C",        "C",    "C",    "C",         "S",      "C",    "C",    "C",     "C", ]
        expected = ' '.join(hyp_aligned)
        expand_align = ExpandedAlignment(ref_aligned, hyp_aligned, alignment, lowercase=True) 
        actual = HypothesisNormalizer.normalizeAligned(expand_align)
        self.assertEqual(actual, expected)
        
    def test_normalize_abbrev_wrong(self):
        ref_aligned = [ "So",  "we",  "learned",  "the",  "majority",      "of",  "anatomic",  "classes",  "taught",  "they",  "do",  "not",  "have",  "a",  "cadaver",   "dissection",  "lab",  ]
        hyp_aligned = [ "so",  "we",  "learned",  "the",  "most jury p.",  "o.",  "anatomy",   "class",    "called",  "they",  "do",  "not",  "have",  "",   "had ever",  "dissection",  "lead", ]
        alignment   = [ "C",   "C",   "C",        "C",    "S",             "S",   "S",         "S",        "S",       "C",     "C",   "C",    "C",     "D",  "S",         "C",           "S",    ]
        expected    = [ "So",  "we",  "learned",  "the",  "most jury p.",  "o.",  "anatomy",   "class",    "called",  "they",  "do",  "not",  "have",  "",   "had ever",  "dissection",  "lead", ]
        expected = ' '.join([ x for x in expected if x ])
        expand_align = ExpandedAlignment(ref_aligned, hyp_aligned, alignment, lowercase=True) 
        actual = HypothesisNormalizer.normalizeAligned(expand_align, fix_casing=True)
        self.assertEqual(actual, expected)
        
    def test_normalize_94(self):
        ref_aligned = [ "Originally",  "the",  "sample",  "was",  "aged",  "18",        "to",  "94",          ]
        hyp_aligned = [ "originally",  "the",  "sample",  "was",  "aged",  "eighteen",  "to",  "ninety four", ]
        alignment   = [ "C",           "C",    "C",       "C",    "C",     "S",         "C",   "S",           ]
        expected    = [ "originally",  "the",  "sample",  "was",  "aged",  "18",  "to",  "94",          ]
        expected = ' '.join([x for x in expected if x])
        expand_align = ExpandedAlignment(ref_aligned, hyp_aligned, alignment, lowercase=True) 
        actual = HypothesisNormalizer.normalizeAligned(expand_align)
        self.assertEqual(actual, expected)
        
    def test_normalize_middle_age(self):
        ref_aligned = [ "They're",   "happier",  "than",  "middle-aged",  "people",  "and",  "younger",  "people",  "certainly", ]
        hyp_aligned = [ "they are",  "happier",  "the",   "middle age",   "people",  "and",  "younger",  "people",  "certainly", ]
        alignment   = [ "S",         "C",        "S",     "S",            "C",       "C",    "C",        "C",       "C",         ]
        expected    = [ "They're",   "happier",  "the",   "middle age",   "people",  "and",  "younger",  "people",  "certainly", ]
        expected = ' '.join([ x for x in expected if x ])
        expand_align = ExpandedAlignment(ref_aligned, hyp_aligned, alignment, lowercase=True) 
        actual = HypothesisNormalizer.normalizeAligned(expand_align)
        self.assertEqual(actual, expected)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()