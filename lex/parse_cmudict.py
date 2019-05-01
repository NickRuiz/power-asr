'''
You can find a copy of CMUDict here
Without syllables: http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict.0.7a
With syllables (98% accuracy): http://webdocs.cs.ualberta.ca/~kondrak/cmudict/cmudict.rep
'''

import re
import json
import string

dictversion = 'cmudict.rep'
with open(dictversion, 'r') as f:
    lex = {}
    for line in f:
        line = line.strip()
        if not line or line[0] == ';':
            continue

        # Parse the line
        tokens = line.split()
        word = re.sub(r'\(\d+\)$', '', tokens[0]).lower()
        phonemes = re.sub(r'\d+', '', ' '.join(tokens[1:])).replace('-', '#').lower()
        if word not in lex:
            # Heuristic: make sure the phonemes are fewer than 2x the letters
            if len(phonemes.split(' ')) > 2 * len(word):
                continue
            lex[word] = phonemes
with open(dictversion+".json", 'w') as fout:
    json.dump(lex, fout, sort_keys=True)