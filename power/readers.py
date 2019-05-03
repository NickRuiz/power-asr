import sys
import json
from power.levenshtein import ExpandedAlignment

class AlignmentReaderJson(object):
	def __init__(self, filepath):
		self.filepath = filepath
		
	def read_alignments(self):
		with open(self.filepath, 'r') as f:
			for line in f:
				yield AlignmentReaderJson.read_json(line)
				
	@staticmethod
	def read_json(jstr):
		in_dict = json.loads(jstr)
		if not in_dict:
			return None
		
		ref = []
		hyp = []
		align = []
		ref_map = []
		hyp_map = []
		
		for i in range(len(in_dict['alignments'])):
			alignment = in_dict['alignments'][i]
			ref.append(alignment['ref'])
			hyp.append(alignment['hyp'])
			align.append(alignment['align'])
			if ref[-1]:
				ref_map.extend([i for r in ref[-1].split()])
			if hyp[-1]:
				hyp_map.extend([i for h in hyp[-1].split()])
		return ExpandedAlignment(ref, hyp, align, ref_map, hyp_map)
		
					
def main(args):
	filename = args[0]
	reader = AlignmentReaderJson(filename)
	for alignment in reader.read_alignments():
		print(alignment)
		print('---')
		
if __name__ == '__main__':
	main(sys.argv[1:])