from collections import defaultdict

class ContractionsEng(object):
    @staticmethod
    def isContraction(word):
        return word in ContractionsEng.contractions
    
    @staticmethod
    def expandOptions(word):
        if ContractionsEng.isContraction(word):
            return ContractionsEng.contractions[word]
        return set()
    
    @staticmethod
    def contractOptions(word):
        if word in ContractionsEng.expansions:
            return ContractionsEng.expansions[word]
        return set()
    
    @staticmethod
    def isDashEquivalent(cont, real):
        options = ContractionsEng.expandOptions(cont)
        return options is not None and real in options 
        
    # From wikipedia
    # http://en.wikipedia.org/wiki/Wikipedia%3aList_of_English_contractions
    contractions = { 
    "ain't": set(["am not", "are not", "is not", "has not", "have not"]),
    "aren't": set(["are not", "am not"]),
    "can't": set(["cannot", "can not"]),     # Manually added "can not"
    "can't've": set(["cannot have"]),
    "'cause": set(["because"]),
    "could've": set(["could have"]),
    "couldn't": set(["could not"]),
    "couldn't've": set(["could not have"]),
    "didn't": set(["did not"]),
    "doesn't": set(["does not"]),
    "don't": set(["do not"]),
    "hadn't": set(["had not"]),
    "hadn't've": set(["had not have"]),
    "hasn't": set(["has not"]),
    "haven't": set(["have not"]),
    "he'd": set(["he had", "he would"]),
    "he'd've": set(["he would have"]),
    "he'll": set(["he shall", "he will"]),
    "he'll've": set(["he shall have", "he will have"]),
    "he's": set(["he has", "he is"]),
    "how'd": set(["how did"]),
    "how'd'y": set(["how do you"]),
    "how'll": set(["how will"]),
    "how's": set(["how has", "how is", "how does"]),
    "i'd": set(["i had", "i would"]),
    "i'd've": set(["i would have"]),
    "i'll": set(["i shall", "i will"]),
    "i'll've": set(["i shall have", "i will have"]),
    "i'm": set(["i am"]),
    "i've": set(["i have"]),
    "isn't": set(["is not"]),
    "it'd": set(["it had", "it would"]),
    "it'd've": set(["it would have"]),
    "it'll": set(["it shall", "it will"]),
    "it'll've": set(["it shall have", "it will have"]),
    "it's": set(["it has", "it is"]),
    "let's": set(["let us"]),
    "ma'am": set(["madam"]),
    "mayn't": set(["may not"]),
    "might've": set(["might have"]),
    "mightn't": set(["might not"]),
    "mightn't've": set(["might not have"]),
    "must've": set(["must have"]),
    "mustn't": set(["must not"]),
    "mustn't've": set(["must not have"]),
    "needn't": set(["need not"]),
    "needn't've": set(["need not have"]),
    "o'clock": set(["of the clock"]),
    "oughtn't": set(["ought not"]),
    "oughtn't've": set(["ought not have"]),
    "shan't": set(["shall not"]),
    "sha'n't": set(["shall not"]),
    "shan't've": set(["shall not have"]),
    "she'd": set(["she had", "she would"]),
    "she'd've": set(["she would have"]),
    "she'll": set(["she shall", "she will"]),
    "she'll've": set(["she shall have", "she will have"]),
    "she's": set(["she has", "she is"]),
    "should've": set(["should have"]),
    "shouldn't": set(["should not"]),
    "shouldn't've": set(["should not have"]),
    "so've": set(["so have"]),
    "so's": set(["so as", "so is"]),
    "that'd": set(["that would", "that had"]),
    "that'd've": set(["that would have"]),
    "that's": set(["that has", "that is"]),
    "there'd": set(["there had", "there would"]),
    "there'd've": set(["there would have"]),
    "there's": set(["there has", "there is"]),
    "they'd": set(["they had", "they would"]),
    "they'd've": set(["they would have"]),
    "they'll": set(["they shall", "they will"]),
    "they'll've": set(["they shall have", "they will have"]),
    "they're": set(["they are"]),
    "they've": set(["they have"]),
    "to've": set(["to have"]),
    "wasn't": set(["was not"]),
    "we'd": set(["we had", "we would"]),
    "we'd've": set(["we would have"]),
    "we'll": set(["we will"]),
    "we'll've": set(["we will have"]),
    "we're": set(["we are"]),
    "we've": set(["we have"]),
    "weren't": set(["were not"]),
    "what'll": set(["what shall", "what will"]),
    "what'll've": set(["what shall have", "what will have"]),
    "what're": set(["what are"]),
    "what's": set(["what has", "what is"]),
    "what've": set(["what have"]),
    "when's": set(["when has", "when is"]),
    "when've": set(["when have"]),
    "where'd": set(["where did"]),
    "where's": set(["where has", "where is"]),
    "where've": set(["where have"]),
    "who'll": set(["who shall", "who will"]),
    "who'll've": set(["who shall have", "who will have"]),
    "who's": set(["who has", "who is"]),
    "who've": set(["who have"]),
    "why's": set(["why has", "why is"]),
    "why've": set(["why have"]),
    "will've": set(["will have"]),
    "won't": set(["will not"]),
    "won't've": set(["will not have"]),
    "would've": set(["would have"]),
    "wouldn't": set(["would not"]),
    "wouldn't've": set(["would not have"]),
    "y'all": set(["you all"]),
    "y'all'd": set(["you all would"]),
    "y'all'd've": set(["you all would have"]),
    "y'all're": set(["you all are"]),
    "y'all've": set(["you all have"]),
    "you'd": set(["you had", "you would"]),
    "you'd've": set(["you would have"]),
    "you'll": set(["you shall", "you will"]),
    "you'll've": set(["you shall have", "you will have"]),
    "you're": set(["you are"]),
    "you've": set(["you have"]),
    }
    
    # Reverse contractions data structure
    expansions = defaultdict(set)
    for key,value_set in contractions.items():
        for value in value_set:
            expansions[value].add(key)
