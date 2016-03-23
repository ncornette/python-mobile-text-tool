#!/usr/bin/env python
# coding=utf-8
from mobileStrings.input import create_format_specs
import os

import update_wordings
import mobileStrings
from mobileStrings.output import IOSResourceWriter, write_csv, write_json, _export_lang_file, \
    write_ios_strings, write_android_strings, AndroidResourceWriter


def main(args):

    in_format_specs = create_format_specs(
        key_col=1,
        exportable_col=9,
        comment_col=3,
        is_comment_col=9,
        translations_start_col=10,
        exportable_rule=lambda v: v == 'mobile',
        is_comment_rule=lambda v: v == 'SCREEN',
        metadata_cols=dict(to_be_translated=2, constraint=7, max_chars=5)
    )

    languages, wordings = mobileStrings.input.read_file(args.input_file, in_format_specs)

    wordings = mobileStrings.input.fix_duplicates(wordings, merge_sections=False)

    mobileStrings.input.trim(wordings)

    if args.android_res_dir:
        _export_lang_file('', 'en', wordings, args.android_res_dir, args.android_resname, AndroidResourceWriter)
        write_android_strings(languages, wordings, args.android_res_dir, args.android_resname)

    if args.ios_res_dir:
        write_ios_strings(languages, wordings, args.ios_res_dir, args.ios_resname)
        _export_lang_file('zh-Hans', 'zh', wordings, args.ios_res_dir, args.ios_resname, IOSResourceWriter)
        _export_lang_file('zh-Hant', 'zh', wordings, args.ios_res_dir, args.ios_resname, IOSResourceWriter)

    out_format_specs = create_format_specs(
        key_col=0,
        exportable_col=1,
        is_comment_col=2,
        comment_col=3,
        metadata_cols=dict(to_be_translated=4, constraint=5, max_chars=6),
        translations_start_col=10
    )

    write_csv(languages, wordings, os.path.join('out', 'wordings.csv'), out_format_specs)
    write_json(languages, wordings, os.path.join('out', 'wordings.json'))

if __name__ == '__main__':
    main(update_wordings.get_parsed_arguments())
