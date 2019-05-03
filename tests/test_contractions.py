import unittest
from normalize import ContractionsEng

class TextToNumEng_Test(unittest.TestCase):
    
    # isContraction tests
    def test_is_contraction_couldnt(self):
        word = "couldn't"
        actual = ContractionsEng.isContraction(word)
        self.assertTrue(actual)
        
    def test_is_contraction_does(self):
        word = "does"
        actual = ContractionsEng.isContraction(word)
        self.assertFalse(actual)
        
    # expandOptions tests
    def test_contraction_options_couldnt(self):
        word = "couldn't"
        expected = set(["could not"])
        actual = ContractionsEng.expandOptions(word)
        self.assertEqual(expected, actual)
        
    # contractOptions tests
    def test_contractOptions_are_not(self):
        words = 'are not'
        expected = set(["ain't", "aren't"])
        actual = ContractionsEng.contractOptions(words)
        self.assertEqual(actual, expected)
        
    def test_contractOptions_who_is(self):
        words = "who is"
        expected = set(["who's"])
        actual = ContractionsEng.contractOptions(words)
        self.assertEqual(actual, expected)
        
    def test_contractOptions_who_was(self):
        words = "who was"
        actual = ContractionsEng.contractOptions(words)
        self.assertTrue(not actual)
        
    # equivalency tests        
    def test_contraction_equivalent_couldnt_true(self):
        cont = "couldn't"
        expand = "could not"
        actual = ContractionsEng.isDashEquivalent(cont, expand)
        self.assertTrue(actual)
        
    def test_contraction_equivalent_couldnt_false(self):
        cont = "couldn't"
        expand = "could"
        actual = ContractionsEng.isDashEquivalent(cont, expand)
        self.assertFalse(actual)
        