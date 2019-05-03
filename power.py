from __future__ import division
import sys
import argparse
import copy
from collections import defaultdict, Counter

from power import writers
from power.aligner import PowerAligner


def main(argv):
    parser = argparse.ArgumentParser("power.py")
    parser.add_argument('--ref', dest='reffile', required=True,
                        help="Define the reference file")
    parser.add_argument('--hyp', dest='hypfile', required=True,
                        help="Define the hypothesis file")
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true', help="Verbose output", default=False)
    parser.add_argument('-o', '--output', dest='output',
                        help="Output file prefix", required=True)
    parser.add_argument('-f', '--format', dest='format', nargs='+', help="Output formats",
                        choices=['sgml', 'snt', 'json', 'align'], default=['snt'])
    parser.add_argument('--print-wer', dest='print_wer', action='store_true',
                        help="Whether to print the original WER info in all of the output formats", default=False)
    parser.add_argument('--compare', dest='compare', action='store_true',
                        help="Print comparison results between POWER and WER", default=False)
    parser.add_argument('--show-phonemes', dest="show_phonemes", action='store_true',
                        help="Show phonetic alignments on error regions", default=False)
    parser.add_argument('--show-confusions', dest="show_confusions",
                        choices=['txt', 'json'], help="Output the phonetic confusions", nargs='+')
    parser.add_argument('--case-sensitive', dest="lowercase", action='store_false',
                        help="Perform case-sensitive alignment", default=True)
    parser.add_argument('--word-align-weights', dest="word_align_weights", required=False, nargs=4, type=int,
                        help='Weights for the Levenshtein word aligner (C S D I)')
    parser.add_argument('--lexicon', dest="lexicon", default=None, required=True, 
                        help="Path to pronunciation lexicon (json key/value dict)")

    #parser.set_defaults(verbose=False, format=['sgml'], print_wer=False, compare_wer=False, show_phonemes=False)

    args = parser.parse_args(argv)

    wer_score_components = Counter()
    power_score_components = Counter()

    wer_confusions = defaultdict(Counter)
    power_confusions = defaultdict(Counter)

    if args.verbose:
        print(args)

    # Open the two files for reading
    with open(args.reffile, 'r') as f_ref, open(args.hypfile, 'r') as f_hyp:
        linecount = 0

        wer_writers = []
        power_writers = []

        for i in range(len(args.format)):
            # Open files for writing POWER
            filepath = "{0}.power.{1}".format(args.output, args.format[i])
            power_writers.append(writers.CreateWriter(
                args.format[i], filepath, args.hypfile, args.reffile))
            if args.print_wer:
                # Open files for writing WER
                filepath = "{0}.wer.{1}".format(args.output, args.format[i])
                wer_writers.append(writers.CreateWriter(
                    args.format[i], filepath, args.hypfile, args.reffile))

        # Assume that line counts match
        for refline in f_ref:
            linecount += 1

            if args.verbose:
                print('===========')
                print('Segment {0:d}:'.format(linecount))
                print('===========')

            refline = refline.strip()
            hypline = f_hyp.readline().strip()
            blank_lines = False
            if not refline and not hypline:
                # Nothing to compare
                blank_lines = True
            else:
                if args.verbose:
                    print('REF: "{0}"'.format(refline))
                    print('HYP: "{0}"'.format(hypline))

                aligner = None
                if args.word_align_weights:
                    keys = ['C', 'S', 'D', 'I']
                    word_align_weights = dict(zip(keys, args.word_align_weights))
                    aligner = PowerAligner(refline, hypline, lowercase=args.lowercase, verbose=args.verbose,
                                            lexicon=args.lexicon, word_align_weights=word_align_weights)
                else:
                    aligner = PowerAligner(refline, hypline, lowercase=args.lowercase, verbose=args.verbose,
                                            lexicon=args.lexicon)
                wer_score_components += Counter(aligner.wer_components)

                if args.print_wer:
                    for writer in wer_writers:
                        if blank_lines:
                            writer.write_blank()
                        else:
                            writer.write(linecount, aligner.wer_components, aligner.wer_alignment)

                if args.verbose:
                    print('WER alignment:')
                    print(aligner.wer_alignment)
                    print('WER:   ', aligner.wer)
                    print('Errors:', aligner.wer_components)
                    print('===============')

                aligner.align()
                power_score_components += Counter(aligner.power_components)

                if args.show_confusions:
                    if args.print_wer:
                        # TODO: Refactor
                        cp = aligner.wer_alignment.confusion_pairs()
                        for key in cp.keys():
                            wer_confusions[key] += cp[key]

                    cp = aligner.power_alignment.confusion_pairs()
                    for key in cp.keys():
                        power_confusions[key] += cp[key]

                if args.verbose:
                    print('Error Regions:')
                    for i in aligner.error_indexes:
                        print(aligner.split_regions[i])
                        print(aligner.phonetic_alignments[i])
                        print('-----')
                    print('===============')
                    print('POWER alignment:')
                    print(aligner.power_alignment)
                    print('POWER: ', aligner.power)
                    print('Errors:', aligner.power_components)
                    print('===============')
                    print("")

            # Write POWER info
            for writer in power_writers:
                if blank_lines:
                    writer.write_blank()
                elif args.show_phonemes:
                    writer.write(linecount, aligner.power_components,
                                 aligner.power_alignment, aligner.phonetic_alignments)
                else:
                    writer.write(linecount, aligner.power_components, aligner.power_alignment)

    # Close all output files
    for writer in wer_writers:
        writer.finalize()
    for writer in power_writers:
        writer.finalize()

    # Compare final WER to POWER
    print("=============")
    print("Final scores:")
    final_wer = (wer_score_components['S'] + wer_score_components['D'] +
                 wer_score_components['I']) / wer_score_components['L']

    final_power = (power_score_components['S'] + power_score_components['D'] +
                   power_score_components['I']) / power_score_components['L']
    print("WER:   {0:1.3f}".format(final_wer))
    print(wer_score_components)
    print("POWER: {0:1.3f}".format(final_power))
    print(power_score_components)

    diff_score = final_power - final_wer
    diff_components = copy.deepcopy(power_score_components)
    diff_components.subtract(wer_score_components)

    print("")
    print("Score component difference (POWER vs WER):")
    print("Diff: {0:1.3f}".format(diff_score))
    print(diff_components)
    print("=============")

    if args.compare:
        writers.CompareWriter.write_comparison("{}.rsum" % args.output, args.hypfile, args.reffile, linecount,
                                               final_power, final_wer, power_score_components, wer_score_components, diff_score, diff_components)
    if args.show_confusions:
        if 'txt' in args.show_confusions:
            writers.ConfusionPairWriter.write(
                "{}.power.conf".format(args.output), args.hypfile, args.reffile, power_confusions)
            if args.print_wer:
                writers.ConfusionPairWriter.write(
                    "{}.wer.conf".format(args.output), args.hypfile, args.reffile, wer_confusions)
        if 'json' in args.show_confusions:
            writers.ConfusionPairWriter.write_json(
                "{}.power.conf.json".format(args.output), args.hypfile, args.reffile, power_confusions)
            if args.print_wer:
                writers.ConfusionPairWriter.write_json(
                    "{}.wer.conf.json".format(args.output), args.hypfile, args.reffile, wer_confusions)


if __name__ == "__main__":
    main(sys.argv[1:])
