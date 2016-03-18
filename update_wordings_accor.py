#!/usr/bin/env python
# coding=utf-8

import update_wordings
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
    main(update_wordings.get_parsed_arguments())
