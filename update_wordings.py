#!/usr/bin/env python
# coding=utf-8

import argparse
from mobileStrings import readers
from mobileStrings import exporters
from mobileStrings.exporters import IOSResourceWriter


def main(args):

    format_specs = readers.FormatSpec(
        1, 9, 3, 9, 10, lambda v: v == 'mobile', lambda v: v == 'SCREEN')

    languages, wordings = readers.read_file(args.input_file, format_specs)

    if args.android_res_dir:
        exporters.android_export(languages, wordings, args.android_res_dir, args.android_resname)

    if args.ios_res_dir:
        exporters.ios_export(languages, wordings, args.ios_res_dir, args.ios_resname)
        exporters._export_lang_file('zh-Hans', 'zh', wordings, args.ios_res_dir, args.ios_resname, IOSResourceWriter)
        exporters._export_lang_file('zh-Hant', 'zh', wordings, args.ios_res_dir, args.ios_resname, IOSResourceWriter)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Export wordings for Android & IOS.')

    args_parser.add_argument('input_file',
                             help=".csv, .xls, .xlsx formats are supported.")

    args_parser.add_argument('--android_res_dir', '-a', default=None, help="resource directory for android strings")
    args_parser.add_argument('--ios_res_dir', '-i', default=None, help="resource directory for android strings")

    args_parser.add_argument('--android-resname', default="strings.xml",
                             help="filename for android resource")

    args_parser.add_argument('--ios-resname', default="i18n.strings",
                             help="filename for ios resource")

    parsed_args = args_parser.parse_args()

    if not (parsed_args.ios_res_dir or parsed_args.android_res_dir):
        args_parser.error('No output specified, please add -a or -i')
    else:
        main(parsed_args)
