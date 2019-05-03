from __future__ import division
import abc
import json
from power.levenshtein import Levenshtein


def CreateWriter(output_type, filepath, hypfile, reffile):
	writer = None
	if output_type == 'sgml':
		writer = SgmlWriter(filepath, hypfile, reffile)
	elif output_type == 'snt':
		writer = SntWriter(filepath, hypfile, reffile)
	elif output_type == 'json':
		writer = JsonWriter(filepath, hypfile, reffile)
	elif output_type == 'align':
		writer = AlignWriter(filepath, hypfile, reffile)
	else:
		raise NotImplementedError("Writer not implemented for %s" % format)
	return writer


class WerWriter(object):
	__metaclass__ = abc.ABCMeta

	def __init__(self, filepath, hypfile, reffile):
		self.out_file = open(filepath, 'w')
		self.filepath = filepath

	@abc.abstractmethod
	def write(self, segid, score_components, expanded_alignment, phonetic_alignments=None):
		return

	def write_blank(self):
		return

	def finalize(self):
		if self.out_file:
			self.out_file.close()
			print('File written to {}'.format(self.filepath))
		self.out_file = None

class AlignWriter(WerWriter):
	def __init__(self, filepath, hypfile, reffile):
		WerWriter.__init__(self, filepath, hypfile, reffile)

	def write(self, segid, score_components, expanded_alignment, phonetic_alignments=None):
		self.out_file.write("{0}\n".format(
			" ".join(expanded_alignment.alignment_expanded())))

	def finalize(self):
		WerWriter.finalize(self)


class SgmlWriter(WerWriter):
	def __init__(self, filepath, hypfile, reffile):
		WerWriter.__init__(self, filepath, hypfile, reffile)
		self.out_file.write('<SYSTEM title="%s" ref_fname="%s" hyp_fname="%s" format="2.0">\n' % (
			hypfile, reffile, hypfile))
		self.out_file.write('<SPEAKER id="spk1">\n')

	def write(self, segid, score_components, expanded_alignment, phonetic_alignments=None):
		self.out_file.write('<PATH id="(%d)" word_cnt="%d">\n' %
		                    (segid, len(expanded_alignment.align)))
		self.out_file.write('%s\n' % ':'.join(['%s,"%s","%s"' % (
			expanded_alignment.align[i], expanded_alignment.s1[i], expanded_alignment.s2[i]) for i in range(len(expanded_alignment.align))]))
		self.out_file.write('</PATH>\n')

	def finalize(self):
		self.out_file.write('</SPEAKER>\n')
		self.out_file.write('</SYSTEM>\n')
		WerWriter.finalize(self)


class JsonWriter(WerWriter):
	def __init__(self, filepath, hypfile, reffile):
		WerWriter.__init__(self, filepath, hypfile, reffile)

	def write(self, segid, score_components, expanded_alignment, phonetic_alignments=None):
		out_dict = dict()
		out_dict['id'] = segid
		out_dict['errorTypes'] = score_components.copy()
		out_dict['errorTypes']['refLength'] = out_dict['errorTypes'].pop('L')
		out_dict['errRate'] = Levenshtein.WER(
			score_components['S'], score_components['D'], score_components['I'], score_components['L'])
		out_dict['alignments'] = []
		for i in range(len(expanded_alignment.align)):
			out_dict['alignments'].append({'align': expanded_alignment.align[i],
                                  'ref': expanded_alignment.s1[i], 'hyp': expanded_alignment.s2[i]})
		self.out_file.write("%s\n" % json.dumps(out_dict))

	def write_blank(self):
		self.out_file.write("%s\n" % json.dumps({}))

	def finalize(self):
		WerWriter.finalize(self)


class SntWriter(WerWriter):
	def __init__(self, filepath, hypfile, reffile):
		WerWriter.__init__(self, filepath, hypfile, reffile)
		self.out_file.write(
			'===============================================================================\n')
		self.out_file.write('             SENTENCE LEVEL REPORT FOR THE SYSTEM:\n')
		self.out_file.write('\tName: %s\n' % hypfile)
		self.out_file.write(
			'===============================================================================\n')
		self.out_file.write('\n\n')

	def write(self, segid, score_components, expanded_alignment, phonetic_alignments=None):
		self.out_file.write('id: (%d)\n' % segid)
		labels = ['C', 'S', 'D', 'I']
		counts = [score_components[label] for label in labels]

		# Print score components
		self.out_file.write('Scores (%s) %s\n' % (' '.join(
			['#%s' % label for label in labels]), ' '.join([str(x) for x in counts])))

		# Print word alignment
		self.out_file.write('%s\n' % expanded_alignment)
		self.out_file.write('\n')

		# Print phonetic alignments
		if phonetic_alignments:
			for palign in [p for p in phonetic_alignments if p]:
				self.out_file.write("%s\n" % palign)
			self.out_file.write('\n')

		# Print statistics
		self.out_file.write('Correct               =  {0:4.1%}   {1}   ({2})\n'.format(
			score_components['C'] / score_components['L'], score_components['C'], score_components['L']))
		self.out_file.write('Substitutions         =  {0:4.1%}   {1}   ({2})\n'.format(
			score_components['S'] / score_components['L'], score_components['S'], score_components['L']))
		self.out_file.write('Deletions             =  {0:4.1%}   {1}   ({2})\n'.format(
			score_components['D'] / score_components['L'], score_components['D'], score_components['L']))
		self.out_file.write('Insertions            =  {0:4.1%}   {1}   ({2})\n'.format(
			score_components['I'] / score_components['L'], score_components['I'], score_components['L']))
		self.out_file.write('\n')
		self.out_file.write('Errors                =  {0:4.1%}   {1}   ({2})\n'.format(Levenshtein.WER(
			score_components['S'], score_components['D'], score_components['I'], score_components['L']), score_components['S']+score_components['D']+score_components['I'], score_components['L']))
		self.out_file.write('\n')
		self.out_file.write('Ref. words            =         {0}   ({1})\n'.format(
			score_components['L'], score_components['L']))
		self.out_file.write('Hyp. words            =         {0}   ({1})\n'.format(
			len(expanded_alignment.s2_string().split()), score_components['L']))
		self.out_file.write('Aligned words         =         {0}   ({1})\n'.format(
			score_components['C']+score_components['S'], score_components['L']))
		self.out_file.write('\n')
		self.out_file.write(
			'-------------------------------------------------------------------------------\n')
		self.out_file.write('\n')

	def finalize(self):
		WerWriter.finalize(self)


class ConfusionPairWriter(WerWriter):
	@staticmethod
	def write(filepath, hypfile, reffile, conf_dict):
		with open(filepath, 'w') as out_file:
			out_file.write("System name: %s\n" % hypfile)
			out_file.write("Ref file   : %s\n" % reffile)

			for key in sorted(conf_dict.keys()):
				for item in sorted(conf_dict[key].keys()):
					out_file.write("%s\t==>\t%s\t%d\n" % (key, item, conf_dict[key][item]))

	@staticmethod
	def write_json(filepath, hypfile, reffile, conf_dict):
		with open(filepath, 'w') as out_file:
			out_file.write("%s\n" % json.dumps(conf_dict))


class CompareWriter:
	@staticmethod
	def write_comparison(filepath, hypfile, reffile, linecount, final_power, final_wer, power_score_components, wer_score_components, diff_score, diff_components):
		with open(filepath, 'w') as out_file:
			out_file.write("System name: %s\n" % hypfile)
			out_file.write("Ref file   : %s\n" % reffile)
			out_file.write("Hyp file   : %s\n" % hypfile)
			out_file.write("""
,---------------------------------------------------------.
|{0:^57}|
|---------------------------------------------------------|
| Metric | # Snt # Wrd |  Corr   Sub    Del    Ins    Err |
|--------+-------------+----------------------------------|
| POWER  | {1:5d} {8:5d} | {9:5d} {10:5d}  {11:5d}  {12:5d}  {13:3.1%} |
| WER    | {1:5d} {2:5d} | {3:5d} {4:5d}  {5:5d}  {6:5d}  {7:3.1%} |
|=========================================================|
| Diff   | {1:5d} {2:5d} | {14:-5d} {15:-5d}  {16:-5d}  {17:-5d}  {18:-3.1%} |
`---------------------------------------------------------'
""".format(hypfile, linecount, wer_score_components['L'], wer_score_components['C'], wer_score_components['S'], wer_score_components['D'], wer_score_components['I'], final_wer, power_score_components['L'], power_score_components['C'], power_score_components['S'], power_score_components['D'], power_score_components['I'], final_power, diff_components['C'], diff_components['S'], diff_components['D'], diff_components['I'], diff_score))
