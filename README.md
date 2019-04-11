# Phonetically-Oriented Word Error Rate aligner (POWER)

Levenshtein-based word alignment and word error rate for ASR that accounts for acoustic confusability.

POWER is a variation to the commonly used Word Error Rate (WER) metric for speech recognition evaluation which incorporates the alignment of phonemes, in the absence of time boundary information. After computing the Levenshtein alignment on words in the reference and hypothesis transcripts, spans of adjacent errors are converted into phonemes with word and syllable boundaries and a phonetic Levenshtein alignment is performed. The phoneme alignment information is used to correct the word alignment labels in each error region. POWER yields similar scores to WER with the added advantages of better word alignments and the ability to capture one-to-many alignments corresponding to homophonic errors in speech recognition hypotheses. These improved alignments allow a better tracing of the impact of Levenshtein error types in speech recognition on downstream tasks such as speech translation.

## Status
This repository is currently empty, but a migration effort will begin soon to move the codebase from a private repository here for the community to benefit. I'm working on an iterative roll-out because of some dependency breaks since I built this back in 2015. Thanks for your patience!

## Current check-ins
Currently the repo only have a simple Levenshtein aligner checked in. See `lev.py` for details.

## Next steps
* Working on reintegrating the phonetic alignment breakdown
* Reintegrate Festival (http://www.cstr.ed.ac.uk/projects/festival/)
* Alternative implementations with CMUDict (http://www.speech.cs.cmu.edu/cgi-bin/cmudict) and Hunspell for syllabification (e.g. https://pyphen.org/) instead of Festival

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
