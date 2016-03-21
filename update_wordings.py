#!/usr/bin/env python
# coding=utf-8

import argparse
import mobileStrings

def get_parsed_arguments():
    args_parser = argparse.ArgumentParser(description='Export wordings for Android & IOS.')
    args_parser.add_argument('input_file',
                             help=".csv, .xls, .xlsx formats are supported.")
    args_parser.add_argument('--android_res_dir', '-a', default=None,
                             help="resource directory for android strings")
    args_parser.add_argument('--ios_res_dir', '-i', default=None,
                             help="resource directory for android strings")
    args_parser.add_argument('--android-resname', default="strings.xml",
                             help="filename for android resource")
    args_parser.add_argument('--ios-resname', default="i18n.strings",
                             help="filename for ios resource")
    parsed_args = args_parser.parse_args()
    if not (parsed_args.ios_res_dir or parsed_args.android_res_dir):
        args_parser.error('No output dir specified, please add -a or -i')

    return parsed_args


def main(args):
    languages, wordings = mobileStrings.input.read_file(args.input_file)

    if args.android_res_dir:
        mobileStrings.output.write_android_strings(languages, wordings, args.android_res_dir, args.android_resname)

    if args.ios_res_dir:
        mobileStrings.output.write_ios_strings(languages, wordings, args.ios_res_dir, args.ios_resname)

if __name__ == '__main__':
    main(get_parsed_arguments())
