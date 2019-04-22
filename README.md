# Phonetically-Oriented Word Error Rate aligner (POWER)

Levenshtein-based word alignment and word error rate for ASR that accounts for acoustic confusability.

POWER is a variation to the commonly used Word Error Rate (WER) metric for speech recognition evaluation which incorporates the alignment of phonemes, in the absence of time boundary information. After computing the Levenshtein alignment on words in the reference and hypothesis transcripts, spans of adjacent errors are converted into phonemes with word and syllable boundaries and a phonetic Levenshtein alignment is performed. The phoneme alignment information is used to correct the word alignment labels in each error region. POWER yields similar scores to WER with the added advantages of better word alignments and the ability to capture one-to-many alignments corresponding to homophonic errors in speech recognition hypotheses. These improved alignments allow a better tracing of the impact of Levenshtein error types in speech recognition on downstream tasks such as speech translation.

## Status
This repository currently contains a simplified version of POWER that doesn't rely directly on TTS. I'm continuing to move parts of the codebase from a private repository here for the community to benefit. It's an iterative roll-out because of some dependency breaks since I built this back in 2015. Thanks for your patience!

## Current check-ins
Currently the repo has:
1. A simple Levenshtein aligner checked in. See `lev.py` for details.
2. The power aligner. See `power.py` for details.

## Example
```
$ python power.py --ref examples/align-words/ref.txt --hyp examples/align-words/hyp.txt --output examples/align-words/results --lexicon lib/lex/cmudict.rep.json

File written to examples/align-words/results.power.snt
=============
Final scores:
WER:   0.326829268293
Counter({'L': 205, 'C': 150, 'S': 39, 'D': 16, 'I': 12})
POWER: 0.326829268293
Counter({'L': 205, 'C': 150, 'S': 52, 'D': 9, 'I': 6})

Score component difference (POWER vs WER):
Diff:  0.0
Counter({'S': 13, 'C': 0, 'L': 0, 'I': -6, 'D': -7})
```

Excerpt from results.power.snt:
```
Scores (#C #S #D #I) 7 8 0 1
REF:  you     know  cadaver  dissection       is    the  traditional  way  of  learning  human  anatomy       
HYP:  seeing  a     cadaver  dissection  and  ease  the  traditional  way  of  loaning   human  and that to me
Eval: S       S     C        C           I    S     C    C            C    C   S         C      S             

Correct               =  58.3%   7   (12)
Substitutions         =  66.7%   8   (12)
Deletions             =  0.0%   0   (12)
Insertions            =  8.3%   1   (12)

Errors                =  75.0%   9   (12)

Ref. words            =         12   (12)
Hyp. words            =         16   (12)
Aligned words         =         15   (12)
```

There are currently a few imperfections due to not using a proper grapheme to phoneme transducer like in Festival. If you see any alignment issues, please open up an Issue.

## Next steps
* Alternative implementations with CMUDict (http://www.speech.cs.cmu.edu/cgi-bin/cmudict) and Hunspell for syllabification (e.g. https://pyphen.org/) instead of Festival (partially complete)
* Reintroduce punctuation splitting and tokenization
* Reintegrate Festival (http://www.cstr.ed.ac.uk/projects/festival/)
* Reintegrate oracle punctuation insertion (i.e. Reference contains punctuation, insert the same punctuation symbols on the hypothesis)

## Papers

When referencing power-asr, please cite [this paper](https://ieeexplore.ieee.org/document/7404808).

```
@inproceedings{power-asr, 
    author={Nicholas Ruiz and Marcello Federico}, 
    booktitle={{2015 IEEE Workshop on Automatic Speech Recognition and Understanding (ASRU)}}, 
    title={Phonetically-oriented word error alignment for speech recognition error analysis in speech translation}, 
    year={2015}, 
    volume={}, 
    number={}, 
    pages={296-302}, 
    keywords={error analysis;speech recognition;word processing;phonetically-oriented word error alignment;speech recognition error analysis;speech translation;word error rate metric;WER metric;speech recognition evaluation;time boundary information;syllable boundaries;phonetic Levenshtein alignment;phoneme alignment information;word alignment labels;phonetically-oriented word error rate;POWER;speech recognition hypothesis;Speech recognition;Error analysis;Speech;Measurement;Matrices;Pragmatics;Analytical models;automatic speech recognition;speech translation;mixed-effects models;error analysis}, 
    doi={10.1109/ASRU.2015.7404808}, 
    ISSN={}, 
    month={Dec},
}
```
