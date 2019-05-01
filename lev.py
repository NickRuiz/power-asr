import sys
import argparse
from power import Levenshtein, ExpandedAlignment


def main(argv):
	parser = argparse.ArgumentParser(description='''Align two sequences of tokens.''')
	parser.add_argument('-c', '--compact', action='store_true', default=False, help="Make the alignment compact")
	parser.add_argument('ref', help='Reference file')
	parser.add_argument('hyp', help='Hypothesis file')

	args = parser.parse_args(argv)

	with open(args.ref, 'r') as fref, open(args.hyp, 'r') as fhyp:
		for ref, hyp in zip(fref, fhyp):
			ref = [x for x in ref.strip().split(' ') if x]
			hyp = [x for x in hyp.strip().split(' ') if x]
			
			lev = Levenshtein.align(ref, hyp) #, reserve_list=PowerAligner.reserve_list, exclusive_sets=PowerAligner.exclusive_sets)
			lev.editops()
			alignment = lev.expandAlign() if not args.compact else lev.expandAlignCompact()
			
			print(alignment)
			print('')

if __name__ == '__main__':
	main(sys.argv[1:])