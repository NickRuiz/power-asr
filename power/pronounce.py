'''
Created on Mar 30, 2015

@author: Nick Ruiz
Assuming you have a file of word sequences, this processes them through Festival to generate pronunciations.

'''
import sys
import json
from itertools import groupby
from normalize import NumToTextEng, splitHyphens
import pyphen

class PronouncerType:
    Base = "base"
    Lexicon = "lexicon"

class PronouncerBase(object):
    def __init__(self):
        pass
    def pronounce(self, words):
        '''G2P conversion'''
        raise NotImplementedError

class PronouncerLex(PronouncerBase):
    '''Lexicon-based pronunciation generator. Looks up words in the lexicon and if they aren't found, uses a hacky alternative.
    NOTE: English-only
    '''
    def __init__(self, lexicon):
        with open(lexicon, 'r') as f:
            self.lexicon = json.load(f)
        self.fallbackDict = pyphen.Pyphen(lang='en_US')

    def pronounce(self, words):
        '''G2P using Pyphen + heuristics'''
        wordsLower = (w.lower() for w in words)
        prons = [self.lexicon[w] if w in self.lexicon else self.alt_pronounce(
            w) for w in wordsLower]
        return "| {0} |".format(' | '.join(prons)).split()

    def alt_pronounce(self, word):
        '''Alternative ways to pronounce the word. Adds simple digit to word conversion'''
        prons = []
        # Split words along hyphens
        wordsSplit = splitHyphens(' '.join(word))
        # Instead of one word, we may have many
        for myword in wordsSplit:
            if myword.isdigit():
                words = NumToTextEng.convert(int(myword)).split()
                pron = ' # '.join((self.pyphen_pronounce(w) for w in words))
            else:
                pron = self.pyphen_pronounce(myword)
            prons.append(pron)
        # Although the hyphenated word is now pronounced as multiple "words", 
        # we treat again as a single word with multiple syllables
        return ' # '.join(prons)
            

    def pyphen_pronounce(self, word):
        ''' Uses pyphen as a back-off to generate a pseudo-hyphenated-pronounciation for words not in the lexicon. '''
        syllables = self.fallbackDict.inserted(word).split('-')
        pron = []
        for syl in syllables:
            m = 0
            n = len(syl)
            sylpron = []
            while m < n:
                pronidx = [(n-i, self.lexicon[syl[m:n-i]])
                        for i in range(n) if syl[m:n-i] in self.lexicon]
                if not pronidx:
                    break
                j, p = pronidx[0]
                sylpron.append(p)
                m = j
            if not sylpron:
                # TODO: No dictionary entries found for this word. Error?
                # Break syl into characters
                sylpron = syl
        
            # Remove duplicate adjacent phonemes
            sylpron = list(i for i, x in groupby(sylpron))
            pron.append(' '.join(sylpron))
        return ' # '.join(pron)
