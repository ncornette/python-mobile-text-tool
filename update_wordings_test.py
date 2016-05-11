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
        self.assertEqual(ur"""&lt; &gt; &amp; %% %% \' \" \’ \n \t \r \f""", output._escape_android_string(
                u'< > & % %% \' " ’ \n \t \r \f'))

        self.assertEqual("%%10 bla 10%% bla 10%%", output._escape_android_string("%10 bla 10% bla 10%"))
        self.assertEqual("%%10 bla 10%% bla 10%%", output._escape_android_string("%%10 bla 10%% bla 10%%"))

    def test_escape_ios(self):
        self.assertEqual(ur"""< > & % %% ' \" ’ \n \t \r \f""", output._escape_ios_string(
                u"< > & % %% ' \" ’ \n \t \r \f"))

        self.assertEqual("%10 bla 10% bla 10%", output._escape_ios_string("%10 bla 10% bla 10%"))
        self.assertEqual("%%10 bla 10%% bla 10%%", output._escape_ios_string("%%10 bla 10%% bla 10%%"))

    def test_read(self):
        languages, wordings = input.read_file('test_translations.xlsx')
        wordings_from_xlsx = input.trimmed(wordings)
        # print 'csv\n'+'\n'.join(repr(w) for w in wordings_from_xlsx)

        wordings_from_xlsx.next()

        next_wording = wordings_from_xlsx.next()
        self.assertEqual(next_wording.key, u'menu.welcome')
        self.assertTrue(next_wording.exportable)
        self.assertFalse(next_wording.is_comment)
        self.assertEqual(next_wording.translations['fr'], u'Bienvenue !')

        next_wording = wordings_from_xlsx.next()
        self.assertEqual(next_wording.key, u'menu.home')
        self.assertTrue(next_wording.exportable)
        self.assertFalse(next_wording.is_comment)
        self.assertEqual(next_wording.translations['de'], u'Start')

        next_wording = wordings_from_xlsx.next()
        self.assertEqual(next_wording.key, u'menu.news')
        self.assertTrue(next_wording.exportable)
        self.assertFalse(next_wording.is_comment)
        self.assertEqual(next_wording.translations['pl'], u'Nowo\u015bci')

        next_wording = wordings_from_xlsx.next()
        self.assertEqual(next_wording.key, u'comment.section')
        self.assertTrue(next_wording.exportable)
        self.assertTrue(next_wording.is_comment)

        next_wording = wordings_from_xlsx.next()
        self.assertEqual(next_wording.key, u'menu.contact')
        self.assertTrue(next_wording.exportable)
        self.assertFalse(next_wording.is_comment)
        self.assertEqual(next_wording.translations['ru'],
                         u'\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u044b')

        wordings_from_xlsx.next()

        next_wording = wordings_from_xlsx.next()
        self.assertEqual(next_wording.key, u'menu.share.not.exported')
        self.assertFalse(next_wording.exportable)
        self.assertFalse(next_wording.is_comment)

        next_wording = wordings_from_xlsx.next()
        self.assertEqual(next_wording.key, u'menu.share')
        self.assertTrue(next_wording.exportable)
        self.assertFalse(next_wording.is_comment)
        self.assertEqual(next_wording.translations['sv'], u'Dela')

    def test_export_import(self):

        android_target = 'test-out/android'
        ios_target = 'test-out/ios'

        shutil.rmtree(android_target, True)
        shutil.rmtree(ios_target, True)

        # EXPORT

        languages, wordings_from_xlsx = input.read_excel('test_translations.xlsx')

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
        input.trimmed(wordings_from_json)
        # print 'xls\n'+'\n'.join(repr(w) for w in wordings_from_json)

        languages, wordings_from_csv = input.read_file('test-out/wordings.csv')
        wordings_from_csv = input.trimmed(wordings_from_csv)
        # print 'json\n'+'\n'.join(repr(w) for w in wordings_from_csv)

        self.maxDiff = None
        self.assertItemsEqual(wordings_from_xlsx, wordings_from_csv)
        self.assertItemsEqual(wordings_from_xlsx, wordings_from_json)

    def _test_convert_test_input(self):
        languages, wordings = input.read_excel('test_translations.xlsx')
        output.write_file(languages, wordings, './test_translations.csv')
        output.write_file(languages, wordings, './test_translations.json')

    def test_unique_keys(self):
        w = input.Wording
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
        w = input.Wording
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
        w = input.Wording
        wordings = [
            w(key='0', translations=OrderedDict(en='hello',   fr='bonjour ')),
            w(key='1', translations=OrderedDict(en='hello\n', fr='bonjour\n\n\n')),
            w(key='2', translations=OrderedDict(en='hello',  fr=' bonjour')),
            w(key='3', translations=OrderedDict(en='\nhello', fr='\n\n\nbonjour'))
        ]

        wordings = input.trimmed(wordings)

        expected_translations = OrderedDict(en='hello', fr='bonjour')
        for w in wordings:
            self.assertEqual(expected_translations, w.translations)

if __name__ == '__main__':
    unittest.main()
