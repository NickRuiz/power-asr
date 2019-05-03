# PSA: All examples in these tests come from TED talks.

import unittest
from power.levenshtein import ExpandedAlignment
from power.punct import PunctInsertOracle


class PunctInsertOracle_Test(unittest.TestCase):

    def test_punct_period_at_end_power(self):
        ref_aligned = [u'A', u'50-year-old',    u'business', u'man', u'lamented', u'to', u'me', u'that', u'he', u'feels', u'he', u"doesn't",  u'have', u'colleagues', u'anymore',  u'at', u'work']
        ref_map =     [  0,    1,               2,           3,      4,           5,     6,     7,       8,     9,        10,    11,          12,      13,            14,          15,    16]
        align =       [u'D', u'S',              u'C',        u'C',   u'S',        u'C',  u'C',  u'C',    u'C',  u'C',     u'C',  u'S',        u'C',    u'C',          u'S',        u'S',  u'S']
        hyp_aligned = [u'',  u'fifty year old', u'business', u'man', u'laments',  u'to', u'me', u'that', u'he', u'feels', u'he', u'does not', u'have', u'colleagues', u'any more', u'it', u'work']
        hyp_map =     [        1,    1,   1,    2,           3,      4,           5,     6,     7,       8,     9,        10,    11,    11,   12,      13,            14,   14,    15,    16]
        expand_align = ExpandedAlignment(ref_aligned, hyp_aligned, align, ref_map, hyp_map, lowercase=True)
        expected =    [u'',  u'fifty year old', u'business', u'man', u'laments',  u'to', u'me', u'that', u'he', u'feels', u'he', u'does not', u'have', u'colleagues', u'any more', u'it', u'work.']
        ref_punct = "A 50-year-old business man lamented to me that he feels he doesn't have colleagues anymore at work."
        actual = PunctInsertOracle.insertPunct(expand_align, ref_punct).s2
        print(actual)
        self.maxDiff = None
        self.assertEqual(actual, expected)
        
    def test_punct_period_at_end_wer(self):
        ref_aligned = [u'A', u'50-year-old', u'business', u'man', u'lamented', u'to', u'me', u'that', u'he', u'feels', u'he', u"doesn't", u'have', u'colleagues', u'anymore', u'at', u'work']
        ref_map =     [0,    1,              2,           3,      4,           5,     6,     7,       8,     9,        10,    11,         12,      13,            14,         15,    16]
        align =       [u'D', u'C',           u'C',        u'C',   u'S',        u'C',  u'C',  u'C',    u'C',  u'C',     u'C',  u'C',       u'C',    u'C',          u'C',       u'S',  u'C']
        hyp_aligned = [u'',  u'50-year-old', u'business', u'man', u'laments',  u'to', u'me', u'that', u'he', u'feels', u'he', u"doesn't", u'have', u'colleagues', u'anymore', u'it', u'work']
        hyp_map =     [      1,              2,           3,      4,           5,     6,     7,       8,     9,        10,    11,         12,      13,            14,         15,    16]
        expected =    [u'',  u'50-year-old', u'business', u'man', u'laments',  u'to', u'me', u'that', u'he', u'feels', u'he', u"doesn't", u'have', u'colleagues', u'anymore', u'it', u'work.']
        ref_punct = "A 50-year-old business man lamented to me that he feels he doesn't have colleagues anymore at work."
        
        expand_align = ExpandedAlignment(ref_aligned, hyp_aligned, align, ref_map, hyp_map, lowercase=True)
        actual = PunctInsertOracle.insertPunct(expand_align, ref_punct).s2
        print(actual)
        self.maxDiff = None
        self.assertEqual(actual, expected)
        
    def test_punct_period_at_end_wer_2(self):
        ref_punct = "So we call this the slicer mode."
        sample_ref     =  ["So", "we", "call", "this", "the", "slicer", "mode", ""   ]
        sample_ref_map =  [0,    1,    2,      3,      4,     5,        6            ]
        sample_align   =  ["C",  "C",  "S",    "C",    "S",   "S",      "S",    "I"  ]
        sample_hyp     =  ["so", "we", "hold", "this", "new", "slice",  "them", "on" ]
        sample_hyp_map =  [0,    1,    2,      3,      4,     5,        6,      7    ]
        sample_hyp_punct= ["so", "we", "hold", "this", "new", "slice",  "them", "on."]
        error_alignment = ExpandedAlignment(sample_ref, sample_hyp,       sample_align, sample_ref_map, sample_hyp_map, lowercase=True)
        expected =        ExpandedAlignment(sample_ref, sample_hyp_punct, sample_align, sample_ref_map, sample_hyp_map, lowercase=True).s2
        actual = PunctInsertOracle.insertPunct(error_alignment, ref_punct).s2
        print(actual)
        self.maxDiff = None
        self.assertEqual(actual, expected)
        
    def test_punct_tokens_at_front_and_end(self):
        sample_ref =     [u'Everyone',  u'who', u'knew', u'me', u'before', u'9/11', u'',       u'',    u'believes', u"I'm",    u'dead', u'I',  u'used', u'to', u'work', u'with', u'a', u'bunch', u'of', u'uptight', u'religious', u'people',   u'so', u'sometimes', u'I', u"didn't", u'wear', u'panties',  u'and', u'just', u'had', u'a', u'big', u'smile', u'and', u'chuckled', u'to', u'myself',   u'',     u'This', u'next', u'one', u'takes', u'a', u'little', u'explanation', u'before', u'I',     u'share', u'it', u'with', u'you']
        sample_ref_map = [0,            1,      2,       3,     4,         5,                          8,           9,         10,      11,    12,      13,    14,      15,      16,   17,       18,    19,         20,           21,          22,    23,           24,   25,        26,      27,          28,     29,      30,     31,   32,     33,       34,     35,          36,    37,                   39,      40,      41,     42,       43,   44,        45,             46,        47,       48,       49,    50,      51]
        sample_align =   [u'C',         u'C',   u'C',    u'C',  u'C',      u'S',    u'I',      u'I',   u'S',        u'S',      u'D',    u'C',  u'C',    u'C',  u'C',    u'C',    u'C', u'C',     u'C',  u'C',       u'C',         u'C',        u'C',  u'C',         u'C', u'C',      u'C',    u'C',        u'S',   u'S',    u'D',   u'C', u'C',   u'C',     u'C',   u'S',        u'C',  u'C',        u'I',    u'C',    u'C',    u'C',   u'C',     u'D', u'C',      u'C',           u'S',      u'S',     u'S',     u'D',  u'C',    u'C']
        sample_hyp =     [u'Everyone',  u'who', u'knew', u'me', u'before', u'nine', u'eleven', u'the', u'believes', u'line',   u'',     u'i',  u'used', u'to', u'work', u'with', u'a', u'bunch', u'of', u'uptight', u'religious', u'people',   u'so', u'sometimes', u'i', u"didn't", u'wear', u'panties',  u'is',  u'that', u'',    u'a', u'big', u'smile', u'and', u'chuckle',  u'to', u'myself',   u'from', u'this', u'next', u'one', u'takes', u'',  u'little', u'explanation', u'of',     u'right', u'here',  u'',   u'with', u'you']
        sample_hyp_map = [0,            1,      2,       3,     4,         5,       6,         7,      8,           9,                  11,    12,      13,    14,      15,      16,   17,       18,    19,         20,           21,          22,    23,           24,   25,        26,      27,          28,     29,              31,   32,     33,       34,     35,          36,    37,          38,      39,      40,      41,     42,             44,        45,             46,        47,       48,              50,      51]
        sample_hyp_punct=[u'"Everyone', u'who', u'knew', u'me', u'before', u'nine', u'eleven', u'the', u'believes', u'line."', u'',     u'"i', u'used', u'to', u'work', u'with', u'a', u'bunch', u'of', u'uptight', u'religious', u'people,',  u'so', u'sometimes', u'i', u"didn't", u'wear', u'panties,', u'is',  u'that', u'',    u'a', u'big', u'smile', u'and', u'chuckle',  u'to', u'myself."', u'from', u'this', u'next', u'one', u'takes', u'',  u'little', u'explanation', u'of',     u'right', u'here',  u'',   u'with', u'you.']
        error_alignment = ExpandedAlignment(sample_ref, sample_hyp,       sample_align, sample_ref_map, sample_hyp_map, lowercase=True)
        ref_punct = u'''"Everyone who knew me before 9/11 believes I'm dead." "I used to work with a bunch of uptight religious people, so sometimes I didn't wear panties, and just had a big smile and chuckled to myself."  This next one takes a little explanation before I share it with you.'''
        expected =        ExpandedAlignment(sample_ref, sample_hyp_punct, sample_align, sample_ref_map, sample_hyp_map, lowercase=True).s2
        actual = PunctInsertOracle.insertPunct(error_alignment, ref_punct).s2
#         print(actual)
        self.maxDiff = None
        self.assertEqual(actual, expected)
        
    def test_punct_tokens_at_front_and_end_short(self):
        sample_ref =     [u'Everyone',  u'who', u'knew', u'me', u'before', u'9/11', u'',       u'',    u'believes', u"I'm",    u'dead']
        sample_ref_map = [0,            1,      2,       3,     4,         5,                          8,           9,         10,    ]
        sample_align =   [u'C',         u'C',   u'C',    u'C',  u'C',      u'S',    u'I',      u'I',   u'S',        u'S',      u'D',  ]
        sample_hyp =     [u'Everyone',  u'who', u'knew', u'me', u'before', u'nine', u'eleven', u'the', u'believes', u'line',   u'',   ]
        sample_hyp_map = [0,            1,      2,       3,     4,         5,       6,         7,      8,           9,                ]
        sample_hyp_punct=[u'"Everyone', u'who', u'knew', u'me', u'before', u'nine', u'eleven', u'the', u'believes', u'line."', u'',   ]
        error_alignment = ExpandedAlignment(sample_ref, sample_hyp,       sample_align, sample_ref_map, sample_hyp_map, lowercase=True)
        ref_punct = u'''"Everyone who knew me before 9/11 believes I'm dead."'''
        expected =        ExpandedAlignment(sample_ref, sample_hyp_punct, sample_align, sample_ref_map, sample_hyp_map, lowercase=True).s2
        actual = PunctInsertOracle.insertPunct(error_alignment, ref_punct).s2
        self.maxDiff = None
        self.assertEqual(actual, expected)
        
    def test_punct_as_separate_words(self):
        sample_ref =     ["The",  "reason",  "they",  "settled",  "out",  "is",  "because",  "it's",  "cheaper",  "to",  "settle",  "than",  "to",  "fight",  "the",  "lawsuit",     "clearly",   "two",  "million",  "dollars",  "cheaper",  "in",  "some",  "cases",   "and",  "much",  "worse",  "if",  "you",  "actually",  "lose"]
        sample_ref_map = [0,       1,        2,       3,          4,      5,     6,          7,        8,          9,    10,        11,      12,    13,       14,     15,            16,          17,      18,         19,        20,         21,    22,      23,        24,     25,      26,       27,    28,     29,          30]
        sample_align =   ["C",    "C",       "C",     "S",        "C",    "C",   "C",        "C",     "C",        "C",   "C",       "C",     "C",   "C",      "C",    "C",           "C",         "C",    "C",        "C",        "C",        "C",   "C",     "C",       "C",    "C",     "C",      "S",   "S",    "C",         "C"]   
        sample_hyp =     ["the",  "reason",  "they",  "settle",   "out",  "is",  "because",  "it's",  "cheaper",  "to",  "settle",  "than",  "to",  "fight",  "the",  "lawsuit",     "clearly",   "two",  "million",  "dollars",  "cheaper",  "in",  "some",  "cases",   "and",  "much",  "worse",  "a",   "few",  "actually",  "lose"]
        sample_hyp_map = [0,       1,        2,       3,          4,      5,     6,          7,        8,          9,    10,        11,      12,    13,       14,     15,            16,          17,      18,         19,        20,         21,    22,      23,        24,     25,      26,       27,    28,     29,          30]
        sample_hyp_punct=["the",  "reason",  "they",  "settle",   "out",  "is",  "because",  "it's",  "cheaper",  "to",  "settle",  "than",  "to",  "fight",  "the",  "lawsuit --",  "clearly,",  "two",  "million",  "dollars",  "cheaper",  "in",  "some",  "cases,",  "and",  "much",  "worse",  "a",   "few",  "actually",  "lose."]
        error_alignment = ExpandedAlignment(sample_ref, sample_hyp,       sample_align, sample_ref_map, sample_hyp_map, lowercase=True)
        ref_punct = '''The reason they settled out is because it's cheaper to settle than to fight the lawsuit -- clearly, two million dollars cheaper in some cases, and much worse if you actually lose.'''
        expected =        ExpandedAlignment(sample_ref, sample_hyp_punct, sample_align, sample_ref_map, sample_hyp_map, lowercase=True).s2
        actual = PunctInsertOracle.insertPunct(error_alignment, ref_punct).s2
        print(actual)
        self.maxDiff = None
        self.assertEqual(actual, expected)
        
    def test_punct_as_separate_words_short(self):
        sample_ref =     ["it's",  "cheaper",  "to",  "settle",  "than",  "to",  "fight",  "the",  "lawsuit",     "clearly"]
        sample_ref_map = [0,       1,          2,      3,        4,       5,     6,        7,        8,           9]
        sample_align =   ["C",     "C",       "C",     "C",      "C",     "C",   "C",      "C",     "C",          "C"]   
        sample_hyp =     ["it's",  "cheaper",  "to",  "settle",  "than",  "to",  "fight",  "the",  "lawsuit",     "clearly"]
        sample_hyp_map = [0,       1,          2,      3,        4,       5,     6,        7,        8,           9]
        sample_hyp_punct=["it's",  "cheaper",  "to",  "settle",  "than",  "to",  "fight",  "the",  "lawsuit --",  "clearly,"]
        error_alignment = ExpandedAlignment(sample_ref, sample_hyp,       sample_align, sample_ref_map, sample_hyp_map, lowercase=True)
        ref_punct = '''it's cheaper to settle than to fight the lawsuit -- clearly,'''
        expected =        ExpandedAlignment(sample_ref, sample_hyp_punct, sample_align, sample_ref_map, sample_hyp_map, lowercase=True).s2
        actual = PunctInsertOracle.insertPunct(error_alignment, ref_punct).s2
        print(actual)
        self.maxDiff = None
        self.assertEqual(actual, expected)
        
    def test_punct_as_separate_words_short2(self):
        sample_ref =     ["it's",  "cheaper",  "to",  "settle",  "than",  "to",  "fight",  "the",  "lawsuit",     "clearly"]
        sample_ref_map = [0,       1,          2,      3,        4,       5,     6,        7,        8,           9]
        sample_align =   ["C",     "C",       "C",     "C",      "C",     "C",   "C",      "C",     "C",          "C"]   
        sample_hyp =     ["it's",  "cheaper",  "to",  "settle",  "than",  "to",  "fight",  "the",  "law suit",     "clearly"]
        sample_hyp_map = [0,       1,          2,      3,        4,       5,     6,        7,        8,           9]
        sample_hyp_punct=["it's",  "cheaper",  "to",  "settle",  "than",  "to",  "fight",  "the",  "law suit --",  "clearly,"]
        error_alignment = ExpandedAlignment(sample_ref, sample_hyp,       sample_align, sample_ref_map, sample_hyp_map, lowercase=True)
        ref_punct = '''it's cheaper to settle than to fight the lawsuit -- clearly,'''
        expected =        ExpandedAlignment(sample_ref, sample_hyp_punct, sample_align, sample_ref_map, sample_hyp_map, lowercase=True).s2
        actual = PunctInsertOracle.insertPunct(error_alignment, ref_punct).s2
        print(actual)
        self.maxDiff = None
        self.assertEqual(actual, expected)
        
    def test_punct_as_separate_words_2deletes(self):
        sample_ref =     ["it's",  "cheaper",  "to",  "settle",   "than",  "to",  "fight",     "the",  "lawsuit",    "clearly" ]
        sample_ref_map = [0,       1,          2,      3,         4,       5,     6,           7,       8,           9         ]
        sample_align =   ["C",     "C",       "C",     "S",       "C",     "C",   "C",         "D",     "D",         "C"       ]   
        sample_hyp =     ["it's",  "cheaper",  "to",  "settled",  "than",  "to",  "fight",     "",      "",          "clearly" ]
        sample_hyp_map = [0,       1,          2,      3,         4,       5,     6,                                 9         ]
        sample_hyp_punct=["it's",  "cheaper",  "to",  "settled",  "than",  "to",  "fight --",  "",      "",          "clearly,"]
        error_alignment = ExpandedAlignment(sample_ref, sample_hyp,       sample_align, sample_ref_map, sample_hyp_map, lowercase=True)
        ref_punct = '''it's cheaper to settle than to fight the lawsuit -- clearly,'''
        expected =        ExpandedAlignment(sample_ref, sample_hyp_punct, sample_align, sample_ref_map, sample_hyp_map, lowercase=True).s2
        actual = PunctInsertOracle.insertPunct(error_alignment, ref_punct).s2
        print(actual)
        self.maxDiff = None
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()