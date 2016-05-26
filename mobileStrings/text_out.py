#!/usr/bin/env python
# coding=utf-8
import simplejson as json

from xml.sax import saxutils
import codecs
from mobileStrings.collection_utils import StreamArray
from mobileStrings.text_in import default_format_specs, Wording, Wordings
import os
from os import makedirs
import re

__author__ = 'nic'

enum_token = re.compile('{(\\d*)}')
single_percent = re.compile('(^|[^%])%([^%]|$)')


def odd(n):
    return n % 2 == 1


def android_token(n):
    return '%' + (n and n + '$') + 's'


def ios_token(n):
    return '%' + (n and n + '$') + '@'


def replace_tokens(s, make_token=None):
    if not make_token:
        return s
    split = enum_token.split(s)
    return ''.join(make_token(v) if odd(i) else v for i, v in enumerate(split))


def normalize_tokens(s):
    s = re.sub(r'%(\d{1,2})\$[@s]', r'{\1}', s)
    s = re.sub(r'%[@s]', r'{}', s)
    return s


def escape_percent(s):
    return single_percent.sub('\\1%%\\2', s)


def _get_words(string):
    s = re.sub(r'[^A-Za-z0-9]', r' ', string)
    s = re.sub(r'([A-Z])([a-z0-9])', r' \1\2', s).strip()
    s = re.sub(r' {2,}', r' ', s)
    return s.split(' ')


def _gen_file_name(default_name, bare_suffix, word_separator, word_func):
    if not bare_suffix:
        return default_name

    suffix = word_separator.join(word_func(s) for s in _get_words(bare_suffix))
    return '{}{}'.format(word_separator, suffix).join(os.path.splitext(default_name))


def _android_res_filename(key, base_filename='strings.xml'):
    return _gen_file_name(base_filename, key, '_', unicode.lower)


def _ios_res_filename(key, base_filename='i18n.strings'):
    return _gen_file_name(base_filename, key, '', unicode.capitalize)


def _escape_android_string(s):

    def escape_chars(text):
        new_android_chars = []
        for c in text:
            if c in ("'", '"', u'’'):
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
    string = normalize_tokens(string)
    string = escape_percent(string)
    string = replace_tokens(string, android_token)
    return string


def _escape_ios_string(s):

    def escape_chars(text):
        new_ios_chars = []
        for c in text:
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
    string = normalize_tokens(string)
    string = replace_tokens(string, ios_token)
    return string


class ANDResourceWriter(object):
    def __init__(self, out_file):
        self.out_file = out_file

    @staticmethod
    def get_lang_dirname(lang):
        return 'values' + (lang and '-' + '-r'.join(lang.split('_')))

    @staticmethod
    def get_res_filename_converter():
        return _android_res_filename

    def write_header(self, lang):
        self.out_file.write(
                u'<?xml version="1.0" encoding="UTF-8"?>\n'
                u'\n'
                u'<!-- Generated Android file for locale : {} -->\n'
                u'\n'
                u'<resources>\n'.format(lang))

    def write_comment(self, comment):
        self.out_file.write(
                u'\n'
                u'  <!-- {} -->\n'.format(comment))

    def write_string(self, key, string):
        self.out_file.write(
                u'  <string name="{}">'.format(key.replace(".", "_")))
        self.out_file.write(_escape_android_string(string))
        self.out_file.write(
                u'</string>\n')

    def write_footer(self):
        self.out_file.write(
                u'</resources>')


class IOSResourceWriter(object):
    def __init__(self, out_file):
        self.out_file = out_file

    @staticmethod
    def get_lang_dirname(lang):
        return '{}.lproj'.format(lang)

    @staticmethod
    def get_res_filename_converter():
        return _ios_res_filename

    def write_header(self, lang):
        self.out_file.write(
                u'// Generated IOS file for locale : {}\n'
                u'\n'
                u'"language"="{}";\n'.format(lang, lang))

    def write_comment(self, comment):
        self.out_file.write(
                u'\n'
                u'// {}\n'.format(comment))

    def write_string(self, key, string):
        self.out_file.write(
                u'"{}"="'.format(key))
        self.out_file.write(_escape_ios_string(string))
        self.out_file.write(
                u'";\n')

    def write_footer(self):
        pass


def _export_lang_file(
        language, from_language, wordings, res_dir, res_filename, writer_type, split_files):
    lang_dirname = writer_type.get_lang_dirname(language).format(language)
    res_lang_dir_path = os.path.join(res_dir, lang_dirname)

    if not os.path.exists(res_lang_dir_path):
        makedirs(res_lang_dir_path)

    f = codecs.open(os.path.join(res_lang_dir_path, res_filename), 'w', 'utf-8')
    writer = writer_type(f)
    try:
        writer.write_header(language)

        for wording in wordings:
            if wording.is_comment:
                if split_files:
                    writer.write_footer()
                    f.close()
                    new_filename = writer_type.get_res_filename_converter()(wording.key,
                                                                            res_filename)
                    f = codecs.open(os.path.join(res_lang_dir_path, new_filename), 'w', 'utf-8')
                    writer = writer_type(f)
                    writer.write_header(language)
                    writer.write_comment(wording.comment)
                else:
                    writer.write_comment(wording.key + ' - ' + wording.comment)
            elif wording.exportable:
                translation = wording.translations.get(from_language)
                if translation:
                    writer.write_string(wording.key, translation.strip())
    finally:
        writer.write_footer()
        f.close()


def _export_languages(languages, wordings, res_dir, res_filename, writer_type, split_files):
    for lang in languages:
        _export_lang_file(lang, lang, wordings, res_dir, res_filename, writer_type, split_files)


def write_android_strings(languages, wordings, res_dir,
                          res_filename='strings.xml',
                          split_files=False):
    _export_languages(languages, wordings, res_dir, res_filename, ANDResourceWriter, split_files)


def write_ios_strings(languages, wordings, res_dir,
                      res_filename='i18n.strings',
                      split_files=False):
    _export_languages(languages, wordings, res_dir, res_filename, IOSResourceWriter, split_files)


def _json_dump(languages, wordings, file_obj, indent=2, dump_func=json.dump):
    dump_func(Wordings(languages, wordings), file_obj, default=StreamArray, indent=indent)


def write_json(languages, wordings, file_or_path, indent=2):
    if hasattr(file_or_path, 'write'):
        _json_dump(languages, wordings, file_or_path, indent)
    else:
        with codecs.open(file_or_path, 'w') as f:
            _json_dump(languages, wordings, f, indent)


def _bool_out(something):
    if something is None:
        return lambda b: b and 'Yes' or ''
    if isinstance(something, (list, tuple)):
        return lambda b: something[0] if b else 'No'
    else:
        return lambda b: something if b else 'No'


# noinspection PyProtectedMember
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

    exportable_rule = _bool_out(format_specs.exportable_value)
    is_comment_rule = _bool_out(format_specs.is_comment_value)

    for wording in wordings:
        row = ['' for _ in range(format_specs.translations_start_col + len(languages))]
        row[format_specs.key_col] = wording.key
        if format_specs.exportable_col == format_specs.is_comment_col:
            row[format_specs.exportable_col] = \
                exportable_rule(wording.exportable) or is_comment_rule(wording.is_comment)
        else:
            row[format_specs.exportable_col] = exportable_rule(wording.exportable)
            row[format_specs.is_comment_col] = is_comment_rule(wording.is_comment)
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


def write_file(languages, wordings, file_path, format_specs=default_format_specs):
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.json':
        write_json(languages, wordings, file_path)
    elif ext.lower() == '.csv':
        write_csv(languages, wordings, file_path, format_specs=format_specs)
