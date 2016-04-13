#!/usr/bin/env python
# coding=utf-8
from functools import partial
import json

from xml.sax import saxutils
import codecs
from flask.json import JSONEncoder
from mobileStrings.collection_utils import StreamArray, StreamArrayJSONEncoder
from mobileStrings.input import default_format_specs, Wording
import os
from os import makedirs
import re

__author__ = 'nic'

enum_token = re.compile('{(\\d*)}')
odd = lambda n: n % 2 == 1

android_token = lambda n: '%' + (n and n + '$') + 's'
ios_token = lambda n: '%' + (n and n + '$') + '@'

def replace_tokens(s, make_token=None):
    if not make_token:
        return s
    split = enum_token.split(s)
    return ''.join(make_token(v) if odd(i) else v for i, v in enumerate(split))

single_percent = re.compile('(^|[^%])%([^%]|$)')
double_percent = lambda s: single_percent.sub('\\1%%\\2', s)

def _escape_android_string(s):

    def escape_chars(string):
        new_android_chars = []
        for c in string:
            if c in ("'",  '"', u'’'):
                new_c = '\\' + c
            else:
                if c == '\n':
                    new_c = r'\n'
                elif c == '\t':
                    new_c = r'\t'
                elif c == '\r':
                    new_c = r'\r'
                elif c == '\f':
                    new_c = r'\f'
                else:
                    new_c = c
            new_android_chars.append(new_c)

        new_android_string = ''.join(new_android_chars)
        return new_android_string

    string = escape_chars(s)
    string = saxutils.escape(string)
    string = double_percent(string)
    string = replace_tokens(string, android_token)
    return string


def _escape_ios_string(s):

    def escape_chars(string):
        new_ios_chars = []
        for c in string:
            if c in ('"',):
                new_c = '\\' + c
            else:
                if c == '\n':
                    new_c = r'\n'
                elif c == '\t':
                    new_c = r'\t'
                elif c == '\r':
                    new_c = r'\r'
                elif c == '\f':
                    new_c = r'\f'
                else:
                    new_c = c
            new_ios_chars.append(new_c)

        new_ios_string = ''.join(new_ios_chars)
        return new_ios_string

    string = escape_chars(s)
    # string = double_percent(string)
    string = replace_tokens(string, ios_token)
    return string

class AndroidResourceWriter(object):
    def __init__(self, out_file):
        self.out_file = out_file

    @staticmethod
    def get_lang_dirname(lang):
        return 'values' + (lang and '-' + '-r'.join(lang.split('_')))

    def write_header(self, lang):
        self.out_file.write(u'<?xml version="1.0" encoding="UTF-8"?>\n<resources>\n')

    def write_comment(self, comment):
        self.out_file.write(u'\n  <!-- {} -->\n'.format(comment))

    def write_string(self, key, string):
        self.out_file.write(u'  <string name="{}">'.format(key.replace(".", "_")))
        self.out_file.write(_escape_android_string(string))
        self.out_file.write(u'</string>\n')

    def write_footer(self):
        self.out_file.write(u'</resources>')


class IOSResourceWriter(object):
    def __init__(self, out_file):
        self.out_file = out_file

    @staticmethod
    def get_lang_dirname(lang):
        return '{}.lproj'.format(lang)

    def write_header(self, lang):
        self.out_file.write(u'//Generated IOS file for locale : {}\n\n"language"="{}";\n'.format(lang, lang))

    def write_comment(self, comment):
        self.out_file.write(u'\n//{}\n'.format(comment))

    def write_string(self, key, string):
        self.out_file.write(u'"{}"="'.format(key))
        self.out_file.write(_escape_ios_string(string))
        self.out_file.write(u'";\n')

    def write_footer(self):
        pass

def _export_lang_file(language, from_language, wordings, res_dir, res_filename, writer_type):
    lang_dirname = writer_type.get_lang_dirname(language).format(language)
    res_lang_dir_path = os.path.join(res_dir, lang_dirname)

    if not os.path.exists(res_lang_dir_path):
        makedirs(res_lang_dir_path)

    with codecs.open(os.path.join(res_lang_dir_path, res_filename), 'w', 'utf-8') as f:
        writer = writer_type(f)
        writer.write_header(language)

        for wording in wordings:
            if wording.is_comment:
                writer.write_comment(wording.key + ' - ' + wording.comment)
            elif wording.exportable:
                translation = wording.translations.get(from_language)
                if translation:
                    writer.write_string(wording.key, translation)

        writer.write_footer()


def _export_languages(languages, wordings, res_dir, res_filename, writer_type):
    for lang in languages:
        _export_lang_file(lang, lang, wordings, res_dir, res_filename, writer_type)


def write_android_strings(languages, wordings, res_dir, res_filename='strings.xml'):
    _export_languages(languages, wordings, res_dir, res_filename, AndroidResourceWriter)


def write_ios_strings(languages, wordings, res_dir, res_filename='i18n.strings'):
    _export_languages(languages, wordings, res_dir, res_filename, IOSResourceWriter)

def _json_dump(languages, wordings, file_obj, indent=2, dump_func=json.dump):
    dump_func(_json_obj(languages, wordings), file_obj, default=StreamArray, indent=indent)


def _json_obj(languages, wordings):
    return {
        'languages': languages,
        'wordings': (w._asdict() for w in wordings)
    }


def write_json(languages, wordings, file_or_path, indent=2):
    if hasattr(file_or_path, 'write'):
        _json_dump(languages, wordings, file_or_path, indent)
    else:
        with codecs.open(file_or_path, 'w') as f:
            _json_dump(languages, wordings, f, indent)


def _write_csv(languages, wordings, file_obj, format_specs):
    """
    :param languages: list(str)
    :param wordings: list(Wording)
    :param file_obj: file
    :param format_specs: FormatSpec
    """
    import csv_unicode
    csv_writer = csv_unicode.UnicodeWriter(file_obj)

    row = [''] * (format_specs.translations_start_col + len(languages))
    row[format_specs.key_col] = Wording._fields[0]
    row[format_specs.exportable_col] = Wording._fields[1]
    row[format_specs.is_comment_col] = Wording._fields[2]
    row[format_specs.comment_col] = Wording._fields[3]

    for k, v in format_specs.metadata_cols.items():
        row[v] = k

    for n, l in enumerate(languages):
        row[format_specs.translations_start_col + n] = l

    csv_writer.writerow(row)

    for wording in wordings:
        row = ['' for _ in range(format_specs.translations_start_col + len(languages))]
        row[format_specs.key_col] = wording.key
        row[format_specs.exportable_col] = wording.exportable and 'Yes' or ''
        row[format_specs.is_comment_col] = wording.is_comment and 'Yes' or ''
        row[format_specs.comment_col] = wording.comment

        for k, v in format_specs.metadata_cols.items():
            row[v] = str(wording.metadata[k])

        for n, l in enumerate(languages):
            row[format_specs.translations_start_col + n] = wording.translations.get(l)

        csv_writer.writerow(row)


def write_csv(languages, wordings, file_or_path, format_specs=default_format_specs):
    if hasattr(file_or_path, 'write'):
        _write_csv(languages, wordings, file_or_path, format_specs)
    else:
        with open(file_or_path, 'wb') as f:
            _write_csv(languages, wordings, f, format_specs)


def write_file(languages, wordings, file_path):
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.json':
        write_json(languages, wordings, file_path)
    elif ext.lower() == '.csv':
        write_csv(languages, wordings, file_path)