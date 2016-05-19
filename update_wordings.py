#!/usr/bin/env python
# coding=utf-8

import argparse
import mobileStrings


def get_parsed_arguments(output_required=True):
    args_parser = argparse.ArgumentParser(description='Export wordings for Android & IOS.',
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args_parser.add_argument('input_file',
                             help=".csv, .xls, .xlsx, .json formats are supported.")
    args_parser.add_argument('-o', '--out-file', default=[], nargs='*',
                             help=".json or .csv output file path")
    args_parser.add_argument('-a', '--android_res_dir', default=None,
                             help="resource directory for android strings")
    args_parser.add_argument('-i', '--ios_res_dir', default=None,
                             help="resource directory for android strings")
    args_parser.add_argument('--android-resname', default="strings.xml",
                             help="filename for android resource")
    args_parser.add_argument('--ios-resname', default="i18n.strings",
                             help="filename for ios resource")
    args_parser.add_argument('-s', '--split-files', default=False, action='store_true',
                             help="Export sections as separate ios and android resource files, "
                                  "comment key is used for naming new files")
    parsed_args = args_parser.parse_args()

    if output_required and \
            not (parsed_args.ios_res_dir or parsed_args.android_res_dir or parsed_args.out_file):
        args_parser.error('No output specified, please add any of -a, -i, -o')

    return parsed_args


def save_from_output_args(args, languages, wordings):
    for f in args.out_file:
        mobileStrings.text_out.write_file(languages, wordings, f)

    if args.android_res_dir:
        mobileStrings.text_out.write_android_strings(languages, wordings, args.android_res_dir,
                                                     args.android_resname, args.split_files)
    if args.ios_res_dir:
        mobileStrings.text_out.write_ios_strings(languages, wordings, args.ios_res_dir,
                                                 args.ios_resname, args.split_files)


def main(args):
    languages, wordings = mobileStrings.text_in.read_file(args.input_file, prefer_generator=False)
    save_from_output_args(args, languages, wordings)


if __name__ == '__main__':
    main(get_parsed_arguments())
