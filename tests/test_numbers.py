import unittest
import traceback
from normalize import TextToNumEng, NumToTextEng

class TextToNumEng_Test(unittest.TestCase):
    
    def test_not_number(self):
        try:
            actual = TextToNumEng.convert('hi there')
            self.assertIsNone(actual)
        except Exception as e:
            self.assertTrue(isinstance(e, Exception))
        
    def test_convert_ones(self):
        expected = 4
        actual = TextToNumEng.convert('four')
        self.assertEqual(actual, expected)
    
    def test_convert_teens(self):
        expected = 19
        actual = TextToNumEng.convert('nineteen')
        self.assertEqual(actual, expected)
        
    def test_convert_tens(self):
        expected = 20
        actual = TextToNumEng.convert('twenty')
        self.assertEqual(actual, expected)
        
    def test_convert_scales(self):
        expected = 500
        actual = TextToNumEng.convert("five hundred")
        self.assertEqual(actual, expected)

    def test_convert_tens_ones(self):
        expected = 92
        actual = TextToNumEng.convert('ninety two')
        self.assertEqual(actual, expected)
        
    def test_convert_hundreds_tens_ones(self):
        expected = 149
        actual = TextToNumEng.convert('one hundred forty nine')
        self.assertEqual(actual, expected)
        
    def test_convert_94(self):
        expected = 94
        actual = TextToNumEng.convert('ninety four')
        self.assertEqual(actual, expected)
        
    def test_convert_999(self):
        try:
            expected = 999
            actual = TextToNumEng.convert('nine hundred ninety nine')
            self.assertEqual(actual, expected)
        except Exception:
            self.assertTrue(False, traceback.format_exc())
        
    def test_convert_millions_thousands_hundreds_tens_ones(self):
        expected = 2050149
        actual = TextToNumEng.convert('two million fifty thousand one hundred forty nine')
        self.assertEqual(actual, expected)
        
    # These 'and' cases are special and should only be considered in this conversion direction.
    def test_convert_hundreds_and_tens_ones(self):
        expected = 249
        actual = TextToNumEng.convert('two hundred and forty nine')
        self.assertEqual(actual, expected)
    
    def test_convert_millions_thousands_hundreds_and_tens_ones(self):
        expected = 2050149
        actual = TextToNumEng.convert('two million fifty thousand one hundred and forty nine')
        self.assertEqual(actual, expected)
        
    def test_number(self):
        expected = 128
        actual = ""
        try:
            actual = TextToNumEng.convert(expected)
            self.assertEqual(expected, actual)
        except TypeError:
            raise
        
    def test_hyphen(self):
        expected = 41
        actual = TextToNumEng.convert('forty-one')
        self.assertEqual(actual, expected)
    
    def test_list_string(self):
        words = 'two million fifty thousand one hundred and forty nine'.split()
        expected = 2050149
        actual = TextToNumEng.convert(words)
        self.assertEqual(actual, expected)
        
    def test_string_empty(self):
        try:
            actual = TextToNumEng.convert('')
            self.fail()
            self.assertIsNone(actual)
        except TypeError:
            pass
        
    def test_invalid_scale(self):
        try:
            actual = TextToNumEng.convert('hundred four')
            self.assertIsNone(actual)
        except Exception as e:
            #print type(e), str(e)
            self.assertTrue(isinstance(e, Exception))
            
    def test_year_1996(self):
        expected = 1996
        actual = TextToNumEng.convertTryYear("nineteen ninety six")
        self.assertEqual(actual, expected)
            
    def test_year_911(self):
        expected = 911
        actual = TextToNumEng.convertTryYear("nine 11")
        self.assertEqual(actual, expected)
            
    def test_year_984(self):
        expected = 984
        actual = TextToNumEng.convertTryYear("nine eighty four")
        self.assertEqual(actual, expected)
        
    def test_year_1992(self):
        expected = 1992
        actual = TextToNumEng.convertTryYear('nineteen ninety two')
        self.assertEqual(actual, expected)
        
    def test_year_2015(self):
        expected = 2015
        actual = TextToNumEng.convertTryYear('twenty fifteen')
        self.assertEqual(actual, expected)
        
    def test_year_invalid(self):
        try:
            actual = TextToNumEng.convertTryYear('nineteen hundred four')
            self.assertIsNone(actual)
        except Exception as e:
            #print type(e), str(e)
            self.assertTrue(isinstance(e, Exception))
            
    def test_year_notyear_number(self):
        try:
            expected = 999
            actual = TextToNumEng.convertTryYear('nine hundred ninety nine')
            self.assertEqual(actual, expected)
        except Exception:
            self.assertTrue(False, traceback.format_exc())
            
        
class NumToTextEng_Test(unittest.TestCase):
    def test_convert_hundreds_tens_ones(self):
        x = 149
        expected = 'one hundred forty nine'
        actual = NumToTextEng.convert(x)
        self.assertEqual(actual, expected)
        
    def test_convert_millions_thousands_hundreds_tens_ones(self):
        expected = 'two million fifty thousand one hundred forty nine'
        actual = NumToTextEng.convert(2050149)
        self.assertEqual(actual, expected)
        
    def test_notnumber(self):
        try:
            actual = NumToTextEng.convert("134sx39")
            self.assertIsNone(actual)
        except TypeError:
            self.assertTrue(True)
            
    def test_convert_2000000(self):
        value = 2000000
        expected = 'two million'
        actual = NumToTextEng.convert(value)
        self.assertEqual(actual, expected)
            
    def test_convertTryYear_2012(self):
        value = 2012
        expected = 'twenty twelve'
        actual = NumToTextEng.convertTryYear(value)
        self.assertEqual(actual, expected)
        
    def test_convertTryYear_611(self):
        value = 611
        expected = 'six eleven'
        actual = NumToTextEng.convertTryYear(value)
        self.assertEqual(actual, expected)
        
    def test_convertTryYear_837(self):
        value = 837
        expected = 'eight thirty seven'
        actual = NumToTextEng.convertTryYear(value)
        self.assertEqual(actual, expected)
        
    def test_convertTryYear_50(self):
        value = 50
        expected = 'fifty'
        try:
            actual = NumToTextEng.convertTryYear(value)
            self.assertEqual(actual, expected)
        except (ValueError, TypeError):
            self.fail()
            
    def test_convert_50(self):
        value = 50
        expected = 'fifty'
        actual = NumToTextEng.convert(value)
        self.assertEqual(actual, expected)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()