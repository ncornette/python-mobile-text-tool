#!/usr/bin/env python
# coding=utf-8
from collections import namedtuple, OrderedDict
import collections
import os

__author__ = 'nic'

Wording = namedtuple("Wording", ['key',
                                 'exportable',
                                 'comment',
                                 'is_comment',
                                 'translations_dict'
                                 ])

class FormatSpec(object):

    def __init__(self, key_col, exportable_col, comment_col, is_comment_col, translations_start_col,
                 exportable_rule=lambda value: bool(value),
                 is_comment_rule=lambda value: bool(value)):
        """
        :param key_col: int
        :param exportable_rule:
        :param comment_col: int
        :param is_comment_rule:
        :param translations_start_col: int
        """
        self.key_col = key_col
        self.exportable_col = exportable_col
        self.is_comment_col = is_comment_col
        self.comment_col = comment_col
        self.translations_start_col = translations_start_col
        self.exportable_rule = exportable_rule
        self.is_comment_rule = is_comment_rule

default_format_specs = FormatSpec(*range(len(Wording._fields)))


class ExcelReader(object):
    def __init__(self, file_path, sheet_index=0):
        import xlrd
        self.book = xlrd.open_workbook(file_path)
        self.sheet = self.book.sheets()[sheet_index]
        self.row_generator = (self.sheet.row_values(row) for row in range(self.sheet.nrows))

    def next(self):
        try:
            return [hasattr(v, 'strip') and v.strip() or v for v in self.row_generator.next()]
        except StopIteration, e:
            self.book.release_resources()
            raise e

    def __iter__(self):
        return self


class CsvReader(object):
    def __init__(self, file_path):
        import csv
        self.csv_file = open(file_path, 'rb')
        self.reader = csv.reader(self.csv_file)

    def next(self):
        return [unicode(v.strip(), 'utf-8') for v in self.reader.next()]

    def __iter__(self):
        return self


def _read(reader, specs=default_format_specs):
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
            new_key = '{}.{}'.format(wording.key, len(duplicate_keys[wording.key]))
            unique_wordings[new_key] = wording
        else:
            unique_wordings[wording.key] = wording

        if wording.exportable or wording.is_comment:
            duplicate_keys[wording.key].append(index+2)

    for key, value in duplicate_keys.items():
        if len(value) > 1:
            print('WARN: duplicate key entry: "{}" found at lines {}'.format(key, ', '.join(str(v) for v in value)))

    return unique_wordings.values()

def read_file(file_path, format_specs=default_format_specs):
    basename, ext = os.path.splitext(file_path.lower())

    if ext == '.csv':
        reader = CsvReader(file_path)
    elif ext.startswith('.xls'):
        reader = ExcelReader(file_path)
    else:
        raise AttributeError("Unknown file type: " + ext)

    return _read(reader, format_specs)
