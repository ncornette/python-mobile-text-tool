#!/usr/bin/env python
# coding=utf-8
import json

from xml.sax import saxutils
import codecs
import os
from os import makedirs

__author__ = 'nic'

def replace_enum_tokens(s, old_token, get_new_token):
    """
    :type s: str
    :type old_token: str
    :type get_new_token: function(token_index)
    """
    split = s.split(old_token)
    if len(split) > 1:
        return len(split) - 1, ''.join((v + ((i < len(split)-1) and get_new_token(i) or '')
                                        for i, v in enumerate(split)))
    else:
        return 0, s


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
    string = string.replace('%@', '{}')
    string = string.replace('%', '%%')
    replace_count1, string = replace_enum_tokens(string, '{}', lambda n: '%{}$s'.format(n + 1))
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
    # string = string.replace('%', '%%')
    replace_count, string = replace_enum_tokens(string, '{}', lambda n: '%@')
    return string


class AndroidResourceWriter(object):
    def __init__(self, out_file):
        self.out_file = out_file

    @staticmethod
    def get_lang_dirname(lang):
        return 'values-{}'.format(lang)

    def write_header(self, lang):
        self.out_file.write(u'<?xml version="1.0" encoding="UTF-8"?>\n<resources>\n')

    def write_comment(self, comment):
        self.out_file.write(u'  <!-- {} -->\n'.format(comment))

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
                writer.write_comment(wording.key)
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


def _write_json(languages, wordings, file_obj, indent=False):
    json.dump(dict(
        languages=languages,
        wordings=[hasattr(w, '_asdict') and w._asdict() or w for w in wordings]), file_obj, indent=indent)

def write_json(languages, wordings, file_or_path, indent=False):
    if hasattr(file_or_path, 'write'):
        _write_json(languages, wordings, file_or_path, indent)
    else:
        with open(file_or_path, 'w') as f:
            _write_json(languages, wordings, f, indent)
