from __future__ import division
import re
from collections import Counter, defaultdict, deque
import itertools


class AlignLabels:
    correct = 'C'
    substitution = 'S'
    insertion = 'I'
    deletion = 'D'
    validOptions = set([correct, substitution, insertion, deletion])


class ExpandedAlignment:
    '''Expands the Levenshtein alignment and lines up the aligned tokens.'''

    def __init__(self, s1, s2, align, s1_map=None, s2_map=None, lowercase=False):
        if not (len(s1) == len(s2) == len(align)):
            raise Exception("Length mismatch: align:{0:d}, s1:{1:d}, s2:{2:d}".format(
                len(align), len(s1), len(s2)))
        if len(align) == 0:
            raise Exception("No alignment: strings are empty")

        self.s1 = s1
        self.s2 = s2
        self.align = align
        self.s1_map = s1_map
        self.s2_map = s2_map
        self.lowercase = lowercase

        if not s1_map or s2_map:
            self.recompute_alignment_maps()

    def __str__(self):
        widths = [max(len(self.s1[i]), len(self.s2[i]))
                  for i in range(len(self.s1))]
        s1_args = zip(widths, self.s1)
        s2_args = zip(widths, self.s2)
        align_args = zip(widths, self.align)

        value = 'REF:  %s\n' % '  '.join(['%-*s' % x for x in s1_args])
        value += 'HYP:  %s\n' % '  '.join(['%-*s' % x for x in s2_args])
        value += 'Eval: %s' % '  '.join(['%-*s' % x for x in align_args])

        return value

    def s1_string(self):
        return ' '.join(self.s1_tokens())

    def s2_string(self):
        return ' '.join(self.s2_tokens())

    def s1_tokens(self):
        return [x for x in self.s1 if x != '']

    def s2_tokens(self):
        return [x for x in self.s2 if x != '']

    def s1_align_tokens(self, i):
        return self.s1[i].split()

    def s2_align_tokens(self, i):
        return self.s2[i].split()

    def ref(self):
        return self.s1_tokens()

    def hyp(self):
        return self.s2_tokens()

    def length(self):
        return len(self.align)

    def pos(self, word):
        s1_idx = [i for i in range(len(self.s1)) if self.s1[i] == word]
        s2_idx = [i for i in range(len(self.s2)) if self.s2[i] == word]

        return s1_idx, s2_idx

    def subsequence(self, i, j, preserve_index=False):
        # TODO: Right now we're losing any s1_map and s2_map components for compatibility reasons. Refactoring necessary.
        scale = 0 if preserve_index else i
        s1_map = [self.s1_map[k] -
                  scale for k in range(len(self.s1_map)) if i <= self.s1_map[k] < j]
        s2_map = [self.s2_map[k] -
                  scale for k in range(len(self.s2_map)) if i <= self.s2_map[k] < j]
        return ExpandedAlignment(self.s1[i:j], self.s2[i:j], self.align[i:j], s1_map, s2_map, lowercase=self.lowercase)

    def split_error_regions(self, error_pattern='[SDI]*S[SDI]+|[SDI]+S[SDI]*'):
        '''
        Splits the object into a list of multiple segments, annotating some as candidate error regions for correction.
        '''
        split_regions = []
        error_indexes = []

        p = re.compile(error_pattern)
        # Find candidate error regions in the current utterance
        # Matches go from left to right
        prev_index = 0

        err_str = ''.join(self.align)
        for match in p.finditer(err_str):
            i, j = match.span()
            if prev_index < i:
                # Previous items are rolled up into a 'correct' segment
                split_regions.append(self.subsequence(prev_index, i))
            # Get the error region
            error_indexes.append(len(split_regions))
            split_regions.append(self.subsequence(i, j))
            prev_index = j

        # Add the trailing segment.
        if prev_index < len(self.align):
            split_regions.append(self.subsequence(prev_index, len(self.align)))
        return split_regions, error_indexes

    def append_alignment(self, expanded_alignment):
        '''
        Concatenates a string alignment to the current.
        '''
        map_offset = self.length()

        self.s1 += expanded_alignment.s1
        self.s2 += expanded_alignment.s2
        self.align += expanded_alignment.align
        if self.s1_map and expanded_alignment.s1_map:
            self.s1_map += [align_pos +
                            map_offset for align_pos in expanded_alignment.s1_map]
        if self.s2_map and expanded_alignment.s2_map:
            self.s2_map += [align_pos +
                            map_offset for align_pos in expanded_alignment.s2_map]

    def recompute_alignment_maps(self):
        '''
        Regenerates s1_map and s2_map based on the alignment info.
        '''
        self.s1_map = []
        self.s2_map = []

        for i in range(self.length()):
            if self.align[i] in (AlignLabels.correct, AlignLabels.substitution, AlignLabels.deletion):
                self.s1_map.extend([i] * len(self.s1[i].split()))
            if self.align[i] in (AlignLabels.correct, AlignLabels.substitution, AlignLabels.insertion):
                self.s2_map.extend([i] * len(self.s2[i].split()))

    def error_rate(self, cluster_on_ref=False):
        '''
        Computes WER or POWER on a given alignment.
        self.s1 is considered to be the reference and self.s2 is the hypothesis.
        '''
        score_components = {AlignLabels.correct: 0, AlignLabels.substitution: 0,
                            AlignLabels.deletion: 0, AlignLabels.insertion: 0, 'L': 0}

        for i in range(self.length()):
            alignment = self.align[i]

            magnitude = 1
            if alignment != AlignLabels.insertion:
                ref_seg_length = len(self.s1[i].split())
                hyp_seg_length = len(self.s2[i].split())

                if cluster_on_ref:
                    # NOTE: This relaxes the penalty of errors like
                    # anatomy -> "and that to me"
                    # And sharply penalizes
                    # "and that to me" -> anatomy
                    # but it might be in better sync with classic WER.
                    magnitude = ref_seg_length
                else:
                    # NOTE: This causes a mismatch between reference length and the number of substitutions! Is this a problem?
                    magnitude = max(ref_seg_length, hyp_seg_length)
                score_components['L'] += ref_seg_length

            score_components[alignment] += magnitude

        if not self.s1:
            # No reference. Error is 100%
            error_rate = 1.0
        else:
            error_rate = (score_components[AlignLabels.substitution] + score_components[AlignLabels.deletion] +
                          score_components[AlignLabels.insertion]) / score_components['L']
        return error_rate, score_components

    def confusion_pairs(self):
        d = defaultdict(Counter)
        for i in range(len(self.align)):
            if self.align[i] == AlignLabels.substitution:
                s1 = self.s1[i]
                s2 = self.s2[i]
                if self.lowercase:
                    s1 = s1.lower()
                    s2 = s2.lower()
                d[s1] += Counter({s2: 1})
        return d

    def alignment_capacity(self):
        '''
        Returns the number of word slots occupied by each alignment point.
        '''
        return [(len(self.s1_align_tokens(i)), len(self.s2_align_tokens(i))) for i in range(self.length())]

    def hyp_oriented_alignment(self, hyp_only=True):
        '''
        TODO: Move to subclass. 
        Returns all alignment tokens. 
        If an S slot is an multiword alignment, duplicates AlignLabels.substitution by the capacity.
        '''
        alignment = []
        ref_align_len, hyp_align_len = zip(*self.alignment_capacity())

        for i in range(self.length()):
            if hyp_only:
                # Treat each hyp token as a substitution error
                alignment.extend(self.align[i] * max(1, hyp_align_len[i]))
            else:
                len_diff = ref_align_len[i] - hyp_align_len[i]
                if len_diff == 0:
                    alignment.extend(self.align[i] * hyp_align_len[i])
                elif len_diff < 0:
                    len_diff = -len_diff
                    alignment.extend(self.align[i] * ref_align_len[i])
                    alignment.extend([AlignLabels.insertion] * len_diff)
                else:
                    alignment.extend(self.align[i] * hyp_align_len[i])
                    alignment.extend([AlignLabels.deletion] * len_diff)
        return alignment


class Levenshtein:
    def __init__(self, lowercase=False):
        self.backMatrix = None
        self.distMatrix = None
        self.dist = -1
        self.s1 = None
        self.s2 = None
        self.edits = None
        self.lowercase = lowercase

    uniformWeights = {AlignLabels.correct: 0, AlignLabels.substitution: 1,
                      AlignLabels.deletion: 1, AlignLabels.insertion: 1}
    wordAlignWeights = {AlignLabels.correct: 0, AlignLabels.substitution: 4,
                        AlignLabels.deletion: 3, AlignLabels.insertion: 3}

    @staticmethod
    def align(ref, hyp, reserve_list=None, exclusive_sets=None, lowercase=False, weights=None, dist_penalty=0.5, dist_penalty_set=None):
        '''
        Creates an alignment with hyp x ref matrix.
        reserve_list defines tokens that may never have 'S' alignments.
        exclusive_sets defines families of tokens that can have 'S' alignments. Anything outside of exclusive_sets can be aligned to any other nonmember.
        '''
        if not weights:
            weights = Levenshtein.uniformWeights
        lev = Levenshtein(lowercase=lowercase)
        lev.s1 = ref
        lev.s2 = hyp

        # If using distance penaties:
        distPenaltyRef = 0
        distPenaltyHyp = 0

        if lowercase:
            ref = [x.lower() for x in ref]
            hyp = [x.lower() for x in hyp]

        #pp = pprint.PrettyPrinter(width=300)
        lev.backMatrix = BackTrackMatrix(len(ref), len(hyp), weights)

        # Starts with 1st word in hyp
        for index2, char2 in enumerate(hyp):

            if dist_penalty_set and char2 not in dist_penalty_set:
                distPenaltyRef += 1
            else:
                distPenaltyRef = 0

            # Loop through columns, corresponding to characters in hyp
            for index1, char1 in enumerate(ref):
                # print 'ref:', index1, char1
                # print 'hyp:', index2, char2

                if dist_penalty_set and char1 not in dist_penalty_set:
                    distPenaltyHyp += 1
                else:
                    distPenaltyHyp = 0

                match_char = AlignLabels.substitution
                # Add insert/delete options
                insPenalty = lev.backMatrix.getWeight(
                    index2, index1+1) + weights[AlignLabels.insertion]
                delPenalty = lev.backMatrix.getWeight(
                    index2+1, index1) + weights[AlignLabels.deletion]

                if dist_penalty_set:
                    # 					insPenalty += dist_penalty * weights[AlignLabels.insertion] * (1 - 1 / (distPenaltyRef + 1))
                    # 					delPenalty += dist_penalty * weights[AlignLabels.deletion] * (1 - 1 / (distPenaltyHyp + 1))

                    insPenalty += (distPenaltyHyp * dist_penalty) * \
                        weights[AlignLabels.insertion]
                    delPenalty += (distPenaltyRef * dist_penalty) * \
                        weights[AlignLabels.deletion]

                opts = [insPenalty,  # I
                        delPenalty,   # D
                        ]

                if char1 == char2:
                    opts.append(lev.backMatrix.getWeight(
                        index2, index1) + weights[AlignLabels.correct])  # C
                    match_char = AlignLabels.correct
                elif not reserve_list or not (char1 in reserve_list or char2 in reserve_list):
                    if exclusive_sets:
                        # Check if char1 and char2 belong to the same exclusive set
                        no_membership_set = set([-1])

                        # Change this to handle multiple set membership
                        char1_sets = set(
                            [k for k in range(len(exclusive_sets)) if char1 in exclusive_sets[k]])
                        if not char1_sets:
                            char1_sets = no_membership_set
                        char2_sets = set(
                            [k for k in range(len(exclusive_sets)) if char2 in exclusive_sets[k]])
                        if not char2_sets:
                            char2_sets = no_membership_set

# 						for k in range(len(exclusive_sets)):
# 							if char1 in exclusive_sets[k]:
# 								char1_set = k
# 							if char2 in exclusive_sets[k]:
# 								char2_set = k
# 						if char1_set == char2_set:
                        if set.intersection(char1_sets, char2_sets):
                            opts.append(lev.backMatrix.getWeight(
                                index2, index1) + weights[AlignLabels.substitution])  # S
                    else:
                        opts.append(lev.backMatrix.getWeight(
                            index2, index1) + weights[AlignLabels.substitution])     # S

                # Get the locally minimum score and edit operation
                minDist = min(opts)
                minIndices = [i for i in reversed(
                    range(len(opts))) if opts[i] == minDist]
# 				minDist, minIndex = min((d, i) for i,d in enumerate(opts))

                # Build the backtrack
                alignLabels = []
                for minIndex in minIndices:
                    if minIndex == 2:
                        alignLabels.append(match_char)
                    elif minIndex == 0:
                        alignLabels.append(AlignLabels.insertion)
                    elif minIndex == 1:
                        alignLabels.append(AlignLabels.deletion)

                lev.backMatrix.addBackTrack(
                    index2+1, index1+1, alignLabels, minDist)  # S/C
                pass

        lev.dist = lev.backMatrix.getWeight(
            lev.backMatrix.hyplen, lev.backMatrix.reflen)
        return lev

    def matchPositions(self, token, token2=None, min_i=None, min_j=None, max_i=None, max_j=None):
        if not min_i:
            min_i = 0
        if not max_i:
            max_i = len(self.s2)

        if not min_j:
            min_j = 0
        if not max_j:
            max_j = len(self.s1)

        if not token2:
            token2 = token

        # Find match positions of token in hyp
        hypIdx = [i+1 for i in range(min_i, max_i) if self.s2[i] == token]
        refIdx = [j+1 for j in range(min_j, max_j) if self.s1[j] == token]

        return list(itertools.product(*[hypIdx, refIdx]))

    def bestPathsGraph(self, minPos=None, maxPos=None):
        """
        Takes all of the best Levenshtein alignment paths and puts them in a graph.
        The graph is weighted by distance, which computes the distance between minPos and maxPos for all paths.
        """
        import networkx as nx
        if not minPos:
            minPos = (0, 0)
        if not maxPos:
            maxPos = (self.backMatrix.hyplen, self.backMatrix.reflen)

        chart = deque()
        chart.appendleft(maxPos)
        # print minPos, maxPos

        G = nx.Graph()

        while chart:
            # print "Chart", chart
            (i, j) = chart.pop()
# 			print self.s1[j-1], self.s2[i-1]

            for alignLabel in self.backMatrix.matrix[i][j].backTrackOptions:
                child = self.backMatrix.matrix[i][j].getBackTrackOffset(
                    alignLabel)
                prev_i = i + child[1][0]
                prev_j = j + child[1][1]

                align = child[0]
                rlabel = self.s1[j-1] if prev_j < j else ''
                hlabel = self.s2[i-1] if prev_i < i else ''

                # Weight applied based on whether (i & prev_i) or (j & prev_j) are along the hull of minPos or maxPos
                weight = 1
                if (i == prev_i and i in (minPos[0], maxPos[0])) or (j == prev_j and j in (minPos[1], maxPos[1])):
                    weight = 0

                # print {'right':(i,j), 'left':(prev_i, prev_j), 'weight':weight, 'labels':(rlabel,hlabel,align)}
                G.add_edge((i, j), (prev_i, prev_j), weight=weight,
                           labels=(rlabel, hlabel, align))
                chart.appendleft((prev_i, prev_j))

        return G

    def expandAlignCompact(self, minPos=None, maxPos=None):
        """
        Using the backtracking matrix, finds all of the paths with the minimum Levenshtein distance score and stores them in a graph.
        Then, it returns the expanded alignment of the shortest path in the graph (which still has the same minimum Lev distance score.
        """
        import networkx as nx
        minPos = (0, 0)
        maxPos = (self.backMatrix.hyplen, self.backMatrix.reflen)

        G = self.bestPathsGraph(minPos, maxPos)
        path = nx.shortest_path(
            G, source=minPos, target=maxPos, weight='weight')

        # Expand the best path into the Levenshtein alignment.
        s1_align, s2_align, align = [list(a) for a in zip(
            *(G[u][v]['labels'] for (u, v) in zip(path[0:], path[1:])))]
        return ExpandedAlignment(s1_align, s2_align, align, lowercase=self.lowercase)

    def editops(self):
        '''
        Records edit distance operations in a compact format, changing s1 to s2.
        '''
        i = self.backMatrix.hyplen
        j = self.backMatrix.reflen
        back = []

        while i > 0 or j > 0:
            op = self.backMatrix.matrix[i][j].getBackTrackOffset()
            off_i, off_j = op[1]
            i += off_i
            j += off_j
            back.append((op[0], (i, j)))

        back.reverse()
        self.edits = back
        return back

    def expandAlign(self):
        '''
        Expands the edit operations to actually align the strings.
        Also contains maps to track the positions of each character in the strings
        to its aligned position.
        '''
        if not self.edits:
            return None

        s1 = []
        s2 = []
        align = []
        s1_map = []
        s2_map = []

        # print "Sequences"
        # print len(self.s1), self.s1
        # print len(self.s2), self.s2

        for op in self.edits:
            a = op[0]
            i, j = op[1]
            # print "i=%d" % i, "j=%d" % j

            # Bugfix for empty hypotheses or reference (reference shouldn't happen)
            c1 = None
            c2 = None
            if -1 < j < len(self.s1):
                c1 = self.s1[j]
            if -1 < i < len(self.s2):
                c2 = self.s2[i]

            if a == AlignLabels.deletion:
                s1.append(c1)
                s2.append('')
                s1_map.append(len(align))
            elif a == AlignLabels.insertion:
                s1.append('')
                s2.append(c2)
                s2_map.append(len(align))
            else:
                s1.append(c1)
                s2.append(c2)
                s1_map.append(len(align))
                s2_map.append(len(align))

            align.append(a)

            # print s1
            # print s2
            # print "---"

        return ExpandedAlignment(s1, s2, align, s1_map, s2_map, lowercase=self.lowercase)

    @staticmethod
    def WER(s, d, i, reflength):
        return (s + d + i) / reflength


class BackTrackMatrix:
    def __init__(self, reflen, hyplen, weights=Levenshtein.uniformWeights):

        self.reflen = reflen
        self.hyplen = hyplen
        self.weights = weights

        self.matrix = [[None] * (reflen+1) for i in range(hyplen+1)]
        self.row_count = hyplen + 1
        self.col_count = reflen + 1

        # Initialize the top corner.
        self.matrix[0][0] = BackTrackSlot(0)

        # Initialize first column.
        for i in range(1, self.row_count):
            self.addBackTrack(i, 0, AlignLabels.insertion,
                              i*weights[AlignLabels.insertion])

        # Initialize columns.
        for j in range(1, self.col_count):
            self.addBackTrack(0, j, AlignLabels.deletion,
                              j*weights[AlignLabels.deletion])

# 	def __str__(self):
# 		value = []
# 		value.extend([x.__str__() for x in self.matrix])
# 		return '\n'.join(value)

    def addBackTrack(self, i, j, alignLabels, weight=1.0):
        self.matrix[i][j] = BackTrackSlot(weight)
        self.matrix[i][j].addOptions(alignLabels)

    def backTrackOptions(self, i, j):
        return self.matrix[i][j]

    def getWeight(self, i, j):
        return self.matrix[i][j].weight

# 	def backTrack(self, i, j, label=None):
# 		if not label:
# 			return self.matrix[i][j].values()[0]
# 		return self.matrix[i][j][label]


class BackTrackSlot:
    def __init__(self, weight):
        self.weight = weight
        self.backTrackOptions = list()

    def __str__(self):
        return "({0}, {1})".format(self.weight, ','.join(list(self.backTrackOptions)))

    def iterOptions(self):
        return iter(self.backTrackOptions)

    def addOption(self, alignLabel):
        if alignLabel not in self.backTrackOptions:
            self.backTrackOptions.append(alignLabel)

    def addOptions(self, alignLabels):
        self.backTrackOptions.extend(
            [x for x in alignLabels if x not in self.backTrackOptions])

    def getBackTrackOffset(self, alignLabel=None):
        if alignLabel:
            # Make sure it exists
            if alignLabel not in AlignLabels.validOptions:
                raise Exception("Invalid backtrack option: %s" % alignLabel)
            if alignLabel not in self.backTrackOptions:
                raise Exception("Illegal backtrack option: %s" % alignLabel)
        else:
            # Just arbitrarily grab the first item
            alignLabel = self.backTrackOptions[0]

        offset = None
        if alignLabel in (AlignLabels.correct, AlignLabels.substitution):
            offset = (-1, -1)
        elif alignLabel == AlignLabels.deletion:
            offset = (0, -1)
        else:
            offset = (-1, 0)
        return (alignLabel, offset)
