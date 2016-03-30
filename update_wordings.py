#!/usr/bin/env python
# coding=utf-8

import argparse
import mobileStrings


def get_parsed_arguments(output_required=True):
    args_parser = argparse.ArgumentParser(description='Export wordings for Android & IOS.',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args_parser.add_argument('input_file',
                             help=".csv, .xls, .xlsx, .json formats are supported.")
    args_parser.add_argument('-o', '--out-file', default=None, nargs='*',
                             help=".json or .csv output file path")
    args_parser.add_argument('-a', '--android_res_dir', default=None,
                             help="resource directory for android strings")
    args_parser.add_argument('-i', '--ios_res_dir', default=None,
                             help="resource directory for android strings")
    args_parser.add_argument('--android-resname', default="strings.xml",
                             help="filename for android resource")
    args_parser.add_argument('--ios-resname', default="i18n.strings",
                             help="filename for ios resource")
    parsed_args = args_parser.parse_args()

    if output_required and \
            not (parsed_args.ios_res_dir or parsed_args.android_res_dir or parsed_args.out_file):
        args_parser.error('No output dir specified, please add any of -a, -i, -o')

    return parsed_args


def main(args):
    languages, wordings = mobileStrings.input.read_file(args.input_file)

    for f in args.out_file:
        mobileStrings.output.write_file(languages, wordings, f)

    if args.android_res_dir:
        mobileStrings.output.write_android_strings(languages, wordings, args.android_res_dir, args.android_resname)

    if args.ios_res_dir:
        mobileStrings.output.write_ios_strings(languages, wordings, args.ios_res_dir, args.ios_resname)

if __name__ == '__main__':
    main(get_parsed_arguments())
