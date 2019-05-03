# Parts of code are adapted from 
# https://www.daniweb.com/software-development/python/code/216839/number-to-word-converter-python

import traceback

class NumbersEnum(object):
    unit = 1
    teens = 2
    tens = 3
    scale = 4
    none = 0 

# TODO: Merge these two classes into one.
class TextToNumEng(object):
    '''
    Currently only works with positive numbers and dates
    Does not work with "twenty one hundred" ==> 2100
    Also doesn't work with month/day combos like "nine eleven" !==> "9/11"
    '''
    # TODO: Don't hardcode everything.
    units = [
            "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", 
        ]
    teens = [
            "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen",
        ]   
    tens = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    scales = ["hundred", "thousand", "million", "billion", "trillion", 
    "quadrillion",  "quintillion",  "sextillion",  "septillion", "octillion", 
    "nonillion",  "decillion",  "undecillion",  "duodecillion",  "tredecillion", 
    "quattuordecillion", "quindecillion", "sexdecillion",  "septendecillion",  "octodecillion", 
    "novemdecillion",  "vigintillion"]
    
    numericWords = set(units + teens + tens + scales)
    
    # Number to word map for calculating numbers
    num2txt_map = dict()
    num2txt_map["and"] = (NumbersEnum.none, 1, 0)
    for idx, word in enumerate(units):    num2txt_map[word] = (NumbersEnum.unit, 1, idx)
    for idx, word in enumerate(teens):    num2txt_map[word] = (NumbersEnum.teens, 1, idx + 10)
    for idx, word in enumerate(tens):     num2txt_map[word] = (NumbersEnum.tens, 1, (idx+2) * 10)
    for idx, word in enumerate(scales):   num2txt_map[word] = (NumbersEnum.scale, 10 ** (idx * 3 or 2), 0)
    
    invalidTransitions = set([
            (NumbersEnum.unit,  NumbersEnum.unit), 
            (NumbersEnum.unit,  NumbersEnum.teens), 
            (NumbersEnum.teens, NumbersEnum.unit), 
            (NumbersEnum.teens, NumbersEnum.tens), 
            (NumbersEnum.tens,  NumbersEnum.teens)
        ])
    
    @staticmethod
    def convertTryYear(textnum):
        '''
        Tries to handle dates if they appear.
        Currently only works with ones, teens, and twenty
        e.g.
        nineteen ninety four
        twelve eleven
        twenty fifteen
        '''
        if not textnum:
            raise TypeError
        
        words = []
        if isinstance(textnum, int) or isinstance(textnum, float):
            return textnum
        elif isinstance(textnum, list):
            words = textnum
        elif isinstance(textnum, str) or isinstance(textnum, unicode):
            words = textnum.split()
        else:
            raise TypeError
        
        first_candidates = set(TextToNumEng.units + TextToNumEng.teens + ['twenty'])
        first_candidates.remove('zero')
        
        if len(words) > 1 and words[0] in first_candidates and words[1] != 'hundred' and (words[1] in TextToNumEng.numericWords or words[1].isdigit()):
            # Split into two parses
            first = words[0]
            # Added special "oh" => 0 case. Like "twelve oh one" => 1201
            second = ' '.join([w for w in words[1:len(words)] if w != "oh"])
            
            combinedNumberStr = ""
            
            try:
                secondNumber = -1
                firstNumber = -1
                if second.isdigit():
                    secondNumber = int(second)
                else:
                    secondNumber = TextToNumEng.convert(second)
                if first.isdigit():
                    firstNumber = int(first)
                else:
                    firstNumber = TextToNumEng.convert(first)
                
#                 secondNumber = TextToNumEng.convert(second)
#                 firstNumber = TextToNumEng.convert(first)
                
                # Concatenate the result
                combinedNumberStr = "{0:d}{1:02d}".format(firstNumber, secondNumber)
                            
                if not (3 <= len(combinedNumberStr) <= 4):
                    raise Exception("Invalid year: {0}".format(combinedNumberStr))
                else:
                    return int(combinedNumberStr)
            except:
                printtraceback.format_exc()
            
        # Either skipped year or year parsing failed.
        return TextToNumEng.convert(words)
              
    
    @staticmethod
    def convert(textnum):
        '''
        Assumes that the number is in a string or list(str). Splits the string into word tokens and tries to convert it to a number
        '''
        if not textnum:
            raise TypeError
        
        words = []
        if isinstance(textnum, int) or isinstance(textnum, float):
            return textnum
        elif isinstance(textnum, list):
            words = textnum
        elif isinstance(textnum, str) or isinstance(textnum, unicode):
            words = textnum.replace('-', ' ').split()
        else:
            raise TypeError
        
        if words[0] in TextToNumEng.scales:
            raise Exception("Illegal number start: %s" % words[0])  
        
        current = result = 0
        prevNumType = NumbersEnum.none
        prevScale = 0
        prevWord = ""
        for word in words:
            if word not in TextToNumEng.num2txt_map:
                raise Exception("Illegal word: " + word)
    
            numtype, scale, increment = TextToNumEng.num2txt_map[word]
            # print numtype, prevNumType
            if prevScale == scale and (numtype == prevNumType or (prevNumType,numtype) in TextToNumEng.invalidTransitions):
                raise Exception("Illegal number transition: {0} => {1}".format(prevWord, word))
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0
            prevNumType = numtype
            prevScale = scale
            prevWord = word
        return result + current
    
        # integer number to english word conversion
    # can be used for numbers as large as 999 vigintillion
    # (vigintillion --> 10 to the power 60)
    # tested with Python24      vegaseat      07dec2006
    @staticmethod
    def int2word(n):
        """
        convert an integer number n into a string of english words
        """
        # break the number into groups of 3 digits using slicing
        # each group representing hundred, thousand, million, billion, ...
        n3 = []
        
        # create numeric string
        ns = str(n)
        for k in range(3, 33, 3):
            r = ns[-k:]
            q = len(ns) - k
            # break if end of ns has been reached
            if q < -2:
                break
            else:
                if  q >= 0:
                    n3.append(int(r[:3]))
                elif q >= -1:
                    n3.append(int(r[:2]))
                elif q >= -2:
                    n3.append(int(r[:1]))
            
        
        #print n3  # test
        
        # break each group of 3 digits into
        # ones, tens/twenties, hundreds
        # and form a string
        nw = ""
        for i, x in enumerate(n3):
            b1 = x % 10
            b2 = (x % 100)//10
            b3 = (x % 1000)//100
            #print b1, b2, b3  # test
            if x == 0:
                continue  # skip
            else:
                t = TextToNumEng.thousands[i]
            if b2 == 0:
                nw = TextToNumEng.ones[b1] + t + nw
            elif b2 == 1:
                nw = TextToNumEng.tens[b1] + t + nw
            elif b2 > 1:
                nw = TextToNumEng.twenties[b2] + TextToNumEng.ones[b1] + t + nw
            if b3 > 0:
                nw = TextToNumEng.ones[b3] + "hundred " + nw
        return nw
    
class NumToTextEng(object):
    units = ["", "one", "two", "three", "four",  "five", 
        "six", "seven", "eight", "nine"]
    teens = ["", "eleven", "twelve", "thirteen",  "fourteen", 
        "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
    tens = ["", "ten", "twenty", "thirty", "forty",
        "fifty", "sixty", "seventy", "eighty", "ninety"]
    thousands = ["","thousand", "million",  "billion",  "trillion", 
        "quadrillion",  "quintillion",  "sextillion",  "septillion", "octillion", 
        "nonillion",  "decillion",  "undecillion",  "duodecillion",  "tredecillion", 
        "quattuordecillion",  "quindecillion", "sexdecillion",  "septendecillion",  "octodecillion", 
        "novemdecillion",  "vigintillion"]
    
    @staticmethod
    def convertTryYear(num):
        first = None
        second = None
        
        num_str = str(num)
        if len(num_str) > 4 or len(num_str) == 0:
            raise ValueError("Invalid date: {0}", num)
        elif len(num_str) >= 3:
            # Check if it could be a year
            if len(num_str) == 3:
                first = int(num_str[0])
                second = int(num_str[1:len(num_str)])
            elif len(num_str) == 4:
                first = int(num_str[0:2])
                second = int(num_str[1:len(num_str)])
                
            if not (first and second):
                raise ValueError("Invalid date: {0:d}", num)
            
            return "{0} {1}".format(NumToTextEng.convert(first), NumToTextEng.convert(second))
        else:
            return NumToTextEng.convert(num)

    
    @staticmethod
    def convert(num):
        if not isinstance(num, int):
            raise TypeError
        
        words = []
        if num == 0:
            words.append("zero")
        else:
            numStr = "%d" % num
            numStrLen = len(numStr)
            groups = (numStrLen + 2) // 3
            numStr = numStr.zfill((groups) * 3)
            for i in range(0, groups*3, 3):
                h = int(numStr[i])
                t = int(numStr[i+1])
                u = int(numStr[i+2])
                g = groups - (i // 3 + 1)
                
                if h >= 1:
                    words.append(NumToTextEng.units[h])
                    words.append("hundred")
                    
                if t > 1:
                    words.append(NumToTextEng.tens[t])
                    if u >= 1:
                        words.append(NumToTextEng.units[u])
                elif t == 1:
                    if u >= 1:
                        words.append(NumToTextEng.teens[u])
                    else:
                        words.append(NumToTextEng.tens[t])
                else:
                    if u >= 1:
                        words.append(NumToTextEng.units[u])
                
                if g >= 1 and (h + t + u) > 0:
                    words.append(NumToTextEng.thousands[g])
        return ' '.join(words)