class Phonemes(object):
    # Vowels
    monophthongs = set(['ao', 'aa', 'iy', 'uw', 'eh', 'ih', 'uh', 'ah', 'ax', 'ae'])
    diphthongs = set(['ey', 'ay', 'ow', 'aw', 'oy'])
    # Add r-colored monophthongs? 
    r_vowels = set(['er', 'axr'])  # The remaining are split into two tokens.
    vowels = set.union(monophthongs, diphthongs, r_vowels)
    
    # Consonants
    c_stops = set(['p','b','t','d','k','g'])
    c_afficates = set(['ch','jh'])
    c_fricatives = set(['f','v','th','dh','s','z','sh','zh','hh'])
    c_nasals = set(['m','em','n','en','ng','eng'])
    c_liquids = set(['l','el','r','dx','nx'])
    c_semivowels = set(['y','w','q'])
    consonants = set.union(c_stops, c_afficates, c_fricatives, c_nasals, c_liquids, c_semivowels)