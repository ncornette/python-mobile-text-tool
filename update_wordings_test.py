#!/usr/bin/env python
# coding=utf-8
from collections import OrderedDict
from mobileStrings import output
from mobileStrings import input

__author__ = 'nic'

import unittest

class MyTestCase(unittest.TestCase):

    def test_replace_tokens_android(self):
        self.assertEqual("blablabla", output._escape_android_string("blablabla"))
        self.assertEqual("bla %1$s blabla", output._escape_android_string("bla {} blabla"))
        self.assertEqual("bla %1$s bla %2$s bla", output._escape_android_string("bla {} bla {} bla"))
        self.assertEqual("bla %1$s blabla", output._escape_android_string("bla %@ blabla"))
        self.assertEqual("bla %1$s bla %2$s bla", output._escape_android_string("bla %@ bla %@ bla"))

    def test_replace_tokens_ios(self):
        self.assertEqual("blablabla", output._escape_ios_string("blablabla"))
        self.assertEqual("bla %@ blabla", output._escape_ios_string("bla {} blabla"))
        self.assertEqual("bla %@ bla %@ bla", output._escape_ios_string("bla {} bla {} bla"))
        self.assertEqual("bla %@ blabla", output._escape_ios_string("bla %@ blabla"))
        self.assertEqual("bla %@ bla %@ bla", output._escape_ios_string("bla %@ bla %@ bla"))

    def test_escape_android(self):
        test_string = u'< > & % \' " ’ \n \t \r \f'
        self.assertEqual(u'&lt; &gt; &amp; %% \\\' \\" \\’ \\n \\t \\r \\f', output._escape_android_string(test_string))
        self.assertEqual(u'< > & % \' \\" ’ \\n \\t \\r \\f', output._escape_ios_string(test_string))

    def test_import(self):
        languages, wordings_from_csv = input.read_file('test_translations.csv')
        input.trim(wordings_from_csv)

        # print 'csv\n'+'\n'.join(repr(w) for w in wordings_from_csv)

        self.assertEqual(wordings_from_csv[1].key, u'menu.welcome')
        self.assertEqual(wordings_from_csv[1].translations['fr'], u'Bienvenue !')

        self.assertEqual(wordings_from_csv[2].key, u'menu.home')
        self.assertEqual(wordings_from_csv[2].translations['de'], u'Start')

        self.assertEqual(wordings_from_csv[3].key, u'menu.news')
        self.assertEqual(wordings_from_csv[3].translations['pl'], u'Nowo\u015bci')

        self.assertEqual(wordings_from_csv[5].key, u'menu.contact')
        self.assertEqual(wordings_from_csv[5].translations['ru'],
                         u'\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u044b')

        languages, wordings_from_xls = input.read_file('test_translations.xlsx')
        input.trim(wordings_from_xls)

        # print 'xls\n'+'\n'.join(repr(w) for w in wordings_from_xls)

        languages, wordings_from_json = input.read_file('test_translations.json')
        input.trim(wordings_from_json)

        # print 'json\n'+'\n'.join(repr(w) for w in wordings_from_json)

        self.assertListEqual(wordings_from_csv, wordings_from_json)
        self.assertListEqual(wordings_from_csv, wordings_from_xls)

    def test_export(self):
        languages, wordings = input.read_file('test_translations.json')

        output.write_android_strings(languages, wordings, 'test-out')
        output.write_ios_strings(languages, wordings, 'test-out')

        output.write_csv(languages, wordings, 'test-out/wordings.csv')
        output.write_json(languages, wordings, 'test-out/out.json')

    def test_unique_keys(self):
        w = input.create_wording
        wordings = [
            w(key='AAA', is_comment=True), w(key='aaa'),
            w(key='BBB', is_comment=True), w(key='bbb'), w(key='ccc'), w(key='aaa'),
            w(key='AAA', is_comment=True), w(key='ddd'),
            w(key='empty.line', exportable=False),
            w(key='eee'),
            w(key='empty.line', exportable=False),
            w(key='fff'),
        ]

        duplicates = input.find_duplicate_wordings(wordings)
        self.assertEqual({'aaa': [1, 5]}, duplicates)

        grouped_wordings = input.unique_wordings_overwrite(wordings)
        self.assertEqual('AAA aaa BBB bbb ccc AAA ddd empty.line eee empty.line fff',
                         ' '.join(w.key for w in grouped_wordings))

    def test_unique_sections(self):
        w = input.create_wording
        wordings = [
            w(key='___'),
            w(key='AAA', is_comment=True), w(key='0'),
            w(key='BBB', is_comment=True), w(key='1'), w(key='2'),
            w(key='CCC', is_comment=True),
            w(key='AAA', is_comment=True), w(key='3'),
        ]

        duplicates = input.find_duplicate_comment_keys(wordings)
        self.assertEqual({'AAA': [1, 7]}, duplicates)

        grouped_wordings = input.group_wordings_by_comment_key(wordings)
        self.assertEqual('___ AAA 0 3 BBB 1 2 CCC', ' '.join(w.key for w in grouped_wordings))

    def test_trim(self):
        w = input.create_wording
        wordings = [
            w(key='0', translations=OrderedDict(en='hello',   fr='bonjour')),
            w(key='1', translations=OrderedDict(en='hello\n', fr='bonjour\n')),
            w(key='2', translations=OrderedDict(en='hello ',  fr='bonjour ')),
            w(key='3', translations=OrderedDict(en=' hello',  fr=' bonjour')),
            w(key='4', translations=OrderedDict(en='\nhello', fr='\nbonjour'))
        ]

        input.trim(wordings)

        expected_translations = OrderedDict(en='hello', fr='bonjour')
        for index, w in enumerate(wordings[:]):
            self.assertEqual(expected_translations, wordings[index].translations)

if __name__ == '__main__':
    unittest.main()
