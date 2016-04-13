#!/usr/bin/env python
# coding=utf-8
from mobileStrings.input import create_format_specs
import os

import update_wordings
import mobileStrings
from mobileStrings.output import IOSResourceWriter, _export_lang_file, \
    write_ios_strings, write_android_strings, AndroidResourceWriter


def main(args):

    # Read Input

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

    _, input_ext = os.path.splitext(args.input_file)
    if input_ext in ('.xls', '.xlsx'):
        languages, wordings = mobileStrings.input.read_excel(args.input_file,
                                                             rows_format_specs=in_format_specs,
                                                             sheet='master')
    else:
        languages, wordings = mobileStrings.input.read_file(args.input_file,
                                                            rows_format_specs=in_format_specs,
                                                            prefer_generator=False)

    # File Export

    for f in args.out_file:
        file_path, _ = os.path.split(f)
        not os.path.exists(file_path) and os.makedirs(file_path)

        _, ext = os.path.splitext(f)
        if ext.lower() == '.csv':
            mobileStrings.output.write_csv(languages, wordings, f, create_format_specs(
                metadata_cols=dict(to_be_translated=4, constraint=5, max_chars=6),
                translations_start_col=10
            ))
        elif ext.lower() == '.json':
            mobileStrings.output.write_json(languages, wordings, f)

    # Mobile Export

    wordings = mobileStrings.input.fix_duplicates(wordings, merge_sections=True)
    wordings = mobileStrings.input.trimmed(wordings)

    if args.android_res_dir:
        write_android_strings(languages, wordings, args.android_res_dir, args.android_resname)
        _export_lang_file('', 'en', wordings, args.android_res_dir, args.android_resname, AndroidResourceWriter)

    if args.ios_res_dir:
        write_ios_strings(languages, wordings, args.ios_res_dir, args.ios_resname)
        _export_lang_file('zh-Hans', 'zh', wordings, args.ios_res_dir, args.ios_resname, IOSResourceWriter)
        _export_lang_file('zh-Hant', 'zh', wordings, args.ios_res_dir, args.ios_resname, IOSResourceWriter)

if __name__ == '__main__':
    main(update_wordings.get_parsed_arguments())
