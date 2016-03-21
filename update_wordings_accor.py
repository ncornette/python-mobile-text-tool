#!/usr/bin/env python
# coding=utf-8

import update_wordings
import mobileStrings
from mobileStrings.output import IOSResourceWriter


def main(args):

    format_specs = mobileStrings.input.FormatSpec(
        1, 9, 3, 9, 10, lambda v: v == 'mobile', lambda v: v == 'SCREEN')

    languages, wordings = mobileStrings.input.read_file(args.input_file, format_specs)

    if args.android_res_dir:
        mobileStrings.output.write_android_strings(languages, wordings, args.android_res_dir, args.android_resname)

    if args.ios_res_dir:
        mobileStrings.output.write_ios_strings(languages, wordings, args.ios_res_dir, args.ios_resname)
        mobileStrings.output._export_lang_file('zh-Hans', 'zh', wordings, args.ios_res_dir, args.ios_resname, IOSResourceWriter)
        mobileStrings.output._export_lang_file('zh-Hant', 'zh', wordings, args.ios_res_dir, args.ios_resname, IOSResourceWriter)

if __name__ == '__main__':
    main(update_wordings.get_parsed_arguments())
