# power-asr
Phonetically-Oriented Word Error Rate

Levenshtein-based word alignment and word error rate that accounts for acoustic confusability.

## Status
This repository is currently empty, but a migration effort will begin soon to move the codebase from a private repository here for the community to benefit. I'm working on an iterative roll-out because of some dependency breaks since I built this back in 2015. Thanks for your patience!

## Current check-ins
Currently the repo only have a simple Levenshtein aligner checked in. See `lev.py` for details.

## Next steps
Working on reintegrating the phonetic alignment breakdown

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
