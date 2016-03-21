#!/usr/bin/env python
# coding=utf-8
from collections import namedtuple, OrderedDict
import json
import collections
import os

__author__ = 'nic'

Wording = namedtuple("Wording", 'key exportable comment is_comment translations')

class FormatSpec(object):

    def __init__(self, key_col, exportable_col, comment_col, is_comment_col, translations_start_col,
                 exportable_rule=lambda value: bool(value),
                 is_comment_rule=lambda value: bool(value),
                 generic_token='{}'):
        """
        :param key_col: int
        :param exportable_rule:
        :param comment_col: int
        :param is_comment_rule:
        :param translations_start_col: int
        """
        self.generic_token = generic_token
        self.key_col = key_col
        self.exportable_col = exportable_col
        self.is_comment_col = is_comment_col
        self.comment_col = comment_col
        self.translations_start_col = translations_start_col
        self.exportable_rule = exportable_rule
        self.is_comment_rule = is_comment_rule

default_format_specs = FormatSpec(*range(len(Wording._fields)))

def _get_csv_rows(file_path):
    import csv
    csv_file = open(file_path, 'rb')
    reader = csv.reader(csv_file)
    for row in reader:
        yield [unicode(v, 'utf-8') for v in row]

def _get_excel_rows(file_path, sheet_index=0):
    import xlrd
    book = xlrd.open_workbook(file_path)
    sheet = book.sheets()[sheet_index]
    for row_index in range(sheet.nrows):
        row = sheet.row_values(row_index)
        yield row


def _read_rows(reader, specs=default_format_specs):
    languages = reader.next()[specs.translations_start_col:]
    wordings = list()

    for row_values in reader:
        key = row_values[specs.key_col]
        is_exportable = specs.exportable_rule(row_values[specs.exportable_col])
        is_comment = specs.is_comment_rule(row_values[specs.is_comment_col])
        comment = row_values[specs.comment_col]

        if row_values:
            w = Wording(key, is_exportable, comment, is_comment,
                        OrderedDict(zip(languages, [v for v in row_values[specs.translations_start_col:]])))

            wordings.append(w)

    return languages, _get_unique_wordings(wordings)

def _get_unique_wordings(wordings):
    unique_wordings = OrderedDict()
    duplicate_keys = collections.defaultdict(lambda: [])

    for index, wording in enumerate(wordings):
        if wording.is_comment:
            # Ignore duplicate keys for comments
            new_key = wording.key+'.'+str(len(duplicate_keys[wording.key]))
            unique_wordings[new_key] = wording
        else:
            unique_wordings[wording.key] = wording

        if wording.exportable or wording.is_comment:
            duplicate_keys[wording.key].append(index+2)

    for key, value in duplicate_keys.items():
        if len(value) > 1:
            print('WARN: duplicate key entry: "' + key + '" found at lines ' +
                  ', '.join(str(v) for v in value))

    return unique_wordings.values()


def _object_hook(dct):
    first_keys = ' '.join([k for k, v in dct][:2])
    if first_keys == 'key exportable':
        return Wording(*[v for k, v in dct])
    return OrderedDict(dct)

def _read_json(file__obj):
    dct = json.load(file__obj, 'utf-8', object_pairs_hook=_object_hook)
    return dct['languages'], dct['wordings']

def read_json(file_or_path):
    if hasattr(file_or_path, 'write'):
        return _read_json(file_or_path)
    else:
        with open(file_or_path, 'r') as f:
            return _read_json(f)

def read_excel(file_path, rows_format_specs=default_format_specs):
    return _read_rows(_get_excel_rows(file_path), rows_format_specs)


def read_csv(file_path, rows_format_specs=default_format_specs):
    return _read_rows(_get_csv_rows(file_path), rows_format_specs)


def read_file(file_path, rows_format_specs=default_format_specs):

    _, ext = os.path.splitext(file_path.lower())

    if ext == '.json':
        return read_json(file_path)
    elif ext == '.csv':
        return read_csv(file_path, rows_format_specs)
    elif ext.startswith('.xls'):
        return read_excel(file_path, rows_format_specs)
    else:
        raise AttributeError("Unknown file type: " + ext)
