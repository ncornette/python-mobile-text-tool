#!/usr/bin/env python
# coding=utf-8
from collections import OrderedDict
import shutil
import re
from mobileStrings import output
from mobileStrings import input
import os

__author__ = 'nic'

import unittest

class MyTestCase(unittest.TestCase):

    def test_tokens_android_generic(self):
        self.assertEqual("blablabla", output._escape_android_string("blablabla"))
        self.assertEqual("bla %s blabla", output._escape_android_string("bla {} blabla"))
        self.assertEqual("bla %s bla %s bla", output._escape_android_string("bla {} bla {} bla"))
        self.assertEqual("bla %1$s bla %2$s bla", output._escape_android_string("bla {1} bla {2} bla"))
        self.assertEqual("bla %2$s bla %1$s bla", output._escape_android_string("bla {2} bla {1} bla"))

    def test_replace_tokens_ios(self):
        self.assertEqual("blablabla", output._escape_ios_string("blablabla"))
        self.assertEqual("bla %@ blabla", output._escape_ios_string("bla {} blabla"))
        self.assertEqual("bla %@ bla %@ bla", output._escape_ios_string("bla {} bla {} bla"))
        self.assertEqual("bla %1$@ bla %2$@ bla", output._escape_ios_string("bla {1} bla {2} bla"))
        self.assertEqual("bla %2$@ bla %1$@ bla", output._escape_ios_string("bla {2} bla {1} bla"))

    def test_escape_android(self):
        test_string = u'< > & % %% \' " ’ \n \t \r \f'
        self.assertEqual(u'&lt; &gt; &amp; %% %% \\\' \\" \\’ \\n \\t \\r \\f', output._escape_android_string(test_string))
        self.assertEqual("%%10 bla 10%% bla 10%%", output._escape_android_string("%10 bla 10% bla 10%"))
        self.assertEqual("%%10 bla 10%% bla 10%%", output._escape_android_string("%%10 bla 10%% bla 10%%"))

    def test_escape_ios(self):
        test_string = u'< > & % %% \' " ’ \n \t \r \f'
        self.assertEqual(u'< > & % %% \' \\" ’ \\n \\t \\r \\f', output._escape_ios_string(test_string))
        self.assertEqual("%10 bla 10% bla 10%", output._escape_ios_string("%10 bla 10% bla 10%"))
        self.assertEqual("%%10 bla 10%% bla 10%%", output._escape_ios_string("%%10 bla 10%% bla 10%%"))

    def test_read(self):
        languages, wordings_from_xlsx = input.read_file('test_translations.xlsx')
        input.trim(wordings_from_xlsx)
        # print 'csv\n'+'\n'.join(repr(w) for w in wordings_from_xlsx)

        self.assertEqual(wordings_from_xlsx[1].key, u'menu.welcome')
        self.assertTrue(wordings_from_xlsx[1].exportable)
        self.assertFalse(wordings_from_xlsx[1].is_comment)
        self.assertEqual(wordings_from_xlsx[1].translations['fr'], u'Bienvenue !')

        self.assertEqual(wordings_from_xlsx[2].key, u'menu.home')
        self.assertTrue(wordings_from_xlsx[2].exportable)
        self.assertFalse(wordings_from_xlsx[2].is_comment)
        self.assertEqual(wordings_from_xlsx[2].translations['de'], u'Start')

        self.assertEqual(wordings_from_xlsx[3].key, u'menu.news')
        self.assertTrue(wordings_from_xlsx[3].exportable)
        self.assertFalse(wordings_from_xlsx[3].is_comment)
        self.assertEqual(wordings_from_xlsx[3].translations['pl'], u'Nowo\u015bci')

        self.assertEqual(wordings_from_xlsx[4].key, u'comment.section')
        self.assertTrue(wordings_from_xlsx[4].exportable)
        self.assertTrue(wordings_from_xlsx[4].is_comment)

        self.assertEqual(wordings_from_xlsx[5].key, u'menu.contact')
        self.assertTrue(wordings_from_xlsx[5].exportable)
        self.assertFalse(wordings_from_xlsx[5].is_comment)
        self.assertEqual(wordings_from_xlsx[5].translations['ru'],
                         u'\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u044b')

        self.assertEqual(wordings_from_xlsx[7].key, u'menu.share.not.exported')
        self.assertFalse(wordings_from_xlsx[7].exportable)
        self.assertFalse(wordings_from_xlsx[7].is_comment)

    def test_export_import(self):

        android_target = 'test-out/android'
        ios_target = 'test-out/ios'

        shutil.rmtree(android_target, True)
        shutil.rmtree(ios_target, True)

        # EXPORT

        languages, wordings_from_xlsx = input.read_file('test_translations.xlsx')

        output.write_android_strings(languages, wordings_from_xlsx, android_target)
        pt_br_android_file_path = os.path.join(android_target, 'values-pt-rBR', 'strings.xml')
        self.assertTrue(os.path.exists(pt_br_android_file_path))
        with open(pt_br_android_file_path) as f:
            content = f.read()
            self.assertTrue(re.search('\n'
                                      '  <!-- comment.section - This is a section -->\n'
                                      '  <string name="menu_contact">Contato</string>', content))

        pt_br_ios_file_path = os.path.join(ios_target, 'pt_BR.lproj', 'i18n.strings')
        output.write_ios_strings(languages, wordings_from_xlsx, ios_target)
        self.assertTrue(os.path.exists(pt_br_ios_file_path))
        with open(pt_br_ios_file_path) as f:
            content = f.read()
            self.assertTrue(re.search('\n'
                                      '//comment.section - This is a section\n'
                                      '"menu.contact"="Contato";\n', content))

        output.write_csv(languages, wordings_from_xlsx, 'test-out/wordings.csv')
        output.write_json(languages, wordings_from_xlsx, 'test-out/wordings.json')

        # READ AND COMPARE

        languages, wordings_from_json = input.read_file('test-out/wordings.json')
        input.trim(wordings_from_json)
        # print 'xls\n'+'\n'.join(repr(w) for w in wordings_from_json)

        languages, wordings_from_csv = input.read_file('test-out/wordings.csv')
        input.trim(wordings_from_csv)
        # print 'json\n'+'\n'.join(repr(w) for w in wordings_from_csv)

        self.assertListEqual(wordings_from_xlsx, wordings_from_csv)
        self.assertListEqual(wordings_from_xlsx, wordings_from_json)

    def test_unique_keys(self):
        w = input.create_wording
        wordings = [
            w(key='SECTION.A', is_comment=True), w(key='a.0'),
            w(key='SECTION.B', is_comment=True), w(key='b.0'), w(key='b.1'), w(key='a.0'),
            w(key='SECTION.A', is_comment=True), w(key='a.2'),
            w(key='empty.line', exportable=False),
            w(key='x.0'),
            w(key='empty.line', exportable=False),
            w(key='x.1'),
        ]

        duplicates = input.find_duplicate_wordings(wordings)
        self.assertEqual({'a.0': [1, 5]}, duplicates)

        grouped_wordings = input.unique_wordings_overwrite(wordings)
        self.assertEqual('SECTION.A a.0 SECTION.B b.0 b.1 SECTION.A a.2 empty.line x.0 empty.line x.1',
                         ' '.join(w.key for w in grouped_wordings))

    def test_unique_sections(self):
        w = input.create_wording
        wordings = [
            w(key='___'),
            w(key='SECTION.A', is_comment=True), w(key='a.0'),
            w(key='SECTION.B', is_comment=True), w(key='b.0'), w(key='b.1'),
            w(key='SECTION.C', is_comment=True),
            w(key='SECTION.A', is_comment=True), w(key='a1'),
        ]

        duplicates = input.find_duplicate_comment_keys(wordings)
        self.assertEqual({'SECTION.A': [1, 7]}, duplicates)

        grouped_wordings = input.group_wordings_by_comment_key(wordings)
        self.assertEqual('___ SECTION.A a.0 a1 SECTION.B b.0 b.1 SECTION.C', ' '.join(w.key for w in grouped_wordings))

    def test_trim(self):
        w = input.create_wording
        wordings = [
            w(key='0', translations=OrderedDict(en='hello',   fr='bonjour ')),
            w(key='1', translations=OrderedDict(en='hello\n', fr='bonjour\n\n\n')),
            w(key='2', translations=OrderedDict(en='hello',  fr=' bonjour')),
            w(key='3', translations=OrderedDict(en='\nhello', fr='\n\n\nbonjour'))
        ]

        input.trim(wordings)

        expected_translations = OrderedDict(en='hello', fr='bonjour')
        for index, w in enumerate(wordings[:]):
            self.assertEqual(expected_translations, wordings[index].translations)

if __name__ == '__main__':
    unittest.main()
