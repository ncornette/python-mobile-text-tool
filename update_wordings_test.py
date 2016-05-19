#!/usr/bin/env python
# coding=utf-8
from collections import OrderedDict
import shutil
import re
from mobileStrings import text_out
from mobileStrings import text_in
from mobileStrings.collection_utils import namedtuple_with_defaults
from mobileStrings.collection_utils import StreamArrayJSONEncoder
import json
import os
import unittest

__author__ = 'nic'


class MyTestCase(unittest.TestCase):

    def test_tokens_android_generic(self):
        self.assertEqual("blablabla",
                         text_out._escape_android_string("blablabla"))
        self.assertEqual("bla %s blabla",
                         text_out._escape_android_string("bla {} blabla"))
        self.assertEqual("bla %s bla %s bla",
                         text_out._escape_android_string("bla {} bla {} bla"))
        self.assertEqual("bla %1$s bla %2$s bla",
                         text_out._escape_android_string("bla {1} bla {2} bla"))
        self.assertEqual("bla %2$s bla %1$s bla",
                         text_out._escape_android_string("bla {2} bla {1} bla"))

    def test_replace_tokens_ios(self):
        self.assertEqual("blablabla",
                         text_out._escape_ios_string("blablabla"))
        self.assertEqual("bla %@ blabla",
                         text_out._escape_ios_string("bla {} blabla"))
        self.assertEqual("bla %@ bla %@ bla",
                         text_out._escape_ios_string("bla {} bla {} bla"))
        self.assertEqual("bla %1$@ bla %2$@ bla",
                         text_out._escape_ios_string("bla {1} bla {2} bla"))
        self.assertEqual("bla %2$@ bla %1$@ bla",
                         text_out._escape_ios_string("bla {2} bla {1} bla"))

    def test_escape_android(self):
        self.assertEqual(ur"""&lt; &gt; &amp; %% %% \' \" \’ \n \t \r \f""",
                         text_out._escape_android_string(u'< > & % %% \' " ’ \n \t \r \f'))
        self.assertEqual("%%10 bla 10%% bla 10%%",
                         text_out._escape_android_string("%10 bla 10% bla 10%"))
        self.assertEqual("%%10 bla 10%% bla 10%%",
                         text_out._escape_android_string("%%10 bla 10%% bla 10%%"))

    def test_escape_ios(self):
        self.assertEqual(ur"""< > & % %% ' \" ’ \n \t \r \f""",
                         text_out._escape_ios_string(u"< > & % %% ' \" ’ \n \t \r \f"))
        self.assertEqual("%10 bla 10% bla 10%",
                         text_out._escape_ios_string("%10 bla 10% bla 10%"))
        self.assertEqual("%%10 bla 10%% bla 10%%",
                         text_out._escape_ios_string("%%10 bla 10%% bla 10%%"))

    def test_resname_android(self):
        self.assertEqual('strings.xml',
                         text_out._android_res_filename(''))
        self.assertEqual('strings_spam.xml',
                         text_out._android_res_filename('spam'))
        self.assertEqual('strings_spam_eggs.xml',
                         text_out._android_res_filename('spam_eggs'))
        self.assertEqual('strings_spam_eggs.xml',
                         text_out._android_res_filename('spam.eggs'))
        self.assertEqual('strings_spam_eggs.xml',
                         text_out._android_res_filename('spam&eggs'))
        self.assertEqual('strings_spam_eggs.xml',
                         text_out._android_res_filename('spamEggs'))
        self.assertEqual('strings_spam_eggs.xml',
                         text_out._android_res_filename('spam_Eggs'))
        self.assertEqual('strings_spam_eggs.xml',
                         text_out._android_res_filename('spam Eggs'))

    def test_resname_ios(self):
        self.assertEqual('i18n.strings',
                         text_out._ios_res_filename(''))
        self.assertEqual('i18nSpam.strings',
                         text_out._ios_res_filename('spam'))
        self.assertEqual('i18nSpamEggs.strings',
                         text_out._ios_res_filename('spam.eggs'))
        self.assertEqual('i18nSpamEggs.strings',
                         text_out._ios_res_filename('spam_eggs'))
        self.assertEqual('i18nSpamEggs.strings',
                         text_out._ios_res_filename('spam&eggs'))
        self.assertEqual('i18nSpamEggs.strings',
                         text_out._ios_res_filename('spam._eggs'))
        self.assertEqual('i18nSpamEggs.strings',
                         text_out._ios_res_filename('spamEggs'))
        self.assertEqual('i18nSpamEggs.strings',
                         text_out._ios_res_filename('spam Eggs'))
        self.assertEqual('i18nSpamEggs.strings',
                         text_out._ios_res_filename('spam eggs'))

    def test_read(self):
        _, wordings = text_in.read_file('test_translations.xlsx')
        wordings_from_xlsx = text_in.trimmed(wordings)

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

    def test_export_android(self):

        android_target = 'test-out/android'

        shutil.rmtree(android_target, True)

        languages, wordings_from_xlsx = text_in.read_excel('test_translations.xlsx')

        text_out.write_android_strings(languages, wordings_from_xlsx, android_target)
        pt_br_android_file_path = os.path.join(android_target, 'values-pt-rBR', 'strings.xml')
        self.assertTrue(os.path.exists(pt_br_android_file_path))
        with open(pt_br_android_file_path) as f:
            content = f.read()
            self.assertTrue(re.search('\n'
                                      '  <!-- comment.section - This is a section -->\n'
                                      '  <string name="menu_contact">Contato</string>', content))

    def test_export_android_multi(self):

        android_target = 'test-out/android'

        shutil.rmtree(android_target, True)

        languages, wordings_from_xlsx = text_in.read_excel('test_translations.xlsx')

        text_out.write_android_strings(
                languages, wordings_from_xlsx, android_target, split_files=True)

        pt_br_android_file_path = os.path.join(
                android_target, 'values-pt-rBR', 'strings_comment_section.xml')

        self.assertTrue(os.path.exists(pt_br_android_file_path))
        with open(pt_br_android_file_path) as f:
            content = f.read()
            self.assertTrue(re.search('\n'
                                      '  <!-- This is a section -->\n'
                                      '  <string name="menu_contact">Contato</string>', content))

    def test_export_ios(self):

        ios_target = 'test-out/ios'

        shutil.rmtree(ios_target, True)

        languages, wordings_from_xlsx = text_in.read_excel('test_translations.xlsx')

        text_out.write_ios_strings(languages, wordings_from_xlsx, ios_target)

        pt_br_ios_file_path = os.path.join(ios_target, 'pt_BR.lproj', 'i18n.strings')

        self.assertTrue(os.path.exists(pt_br_ios_file_path))
        with open(pt_br_ios_file_path) as f:
            content = f.read()
            self.assertTrue(re.search('\n'
                                      '// comment.section - This is a section\n'
                                      '"menu.contact"="Contato";\n', content))

    def test_export_ios_multi(self):

        ios_target = 'test-out/ios'

        shutil.rmtree(ios_target, True)

        languages, wordings_from_xlsx = text_in.read_excel('test_translations.xlsx')

        text_out.write_ios_strings(
                languages, wordings_from_xlsx, ios_target, split_files=True)

        pt_br_ios_file_path = os.path.join(
                ios_target, 'pt_BR.lproj', 'i18nCommentSection.strings')

        self.assertTrue(os.path.exists(pt_br_ios_file_path))
        with open(pt_br_ios_file_path) as f:
            content = f.read()
            self.assertTrue(re.search('\n'
                                      '// This is a section\n'
                                      '"menu.contact"="Contato";\n', content))

    def test_export_import(self):

        languages, wordings_from_xlsx = text_in.read_excel('test_translations.xlsx')

        text_out.write_csv(languages, wordings_from_xlsx, 'test-out/wordings.csv')
        text_out.write_json(languages, wordings_from_xlsx, 'test-out/wordings.json')

        # READ AND COMPARE

        languages, wordings_from_json = text_in.read_file('test-out/wordings.json')
        text_in.trimmed(wordings_from_json)

        languages, wordings_from_csv = text_in.read_file('test-out/wordings.csv')
        wordings_from_csv = text_in.trimmed(wordings_from_csv)

        self.maxDiff = None
        self.assertItemsEqual(wordings_from_xlsx, wordings_from_csv)
        self.assertItemsEqual(wordings_from_xlsx, wordings_from_json)

    def test_convert_test_input(self):
        languages, wordings = text_in.read_excel('test_translations.xlsx')

        text_out.write_file(languages, wordings, './test_translations.csv')
        self.assertTrue(os.path.exists('./test_translations.csv'))
        self.assertGreater(os.stat('./test_translations.csv').st_size, 0)

        text_out.write_file(languages, wordings, './test_translations.json')
        self.assertTrue(os.path.exists('./test_translations.json'))
        self.assertGreater(os.stat('./test_translations.json').st_size, 0)

    def test_unique_keys(self):
        w = text_in.Wording
        wordings = [
            w(key='SECTION.A', is_comment=True), w(key='a.0'),
            w(key='SECTION.B', is_comment=True), w(key='b.0'), w(key='b.1'), w(key='a.0'),
            w(key='SECTION.A', is_comment=True), w(key='a.2'),
            w(key='empty.line', exportable=False),
            w(key='x.0'),
            w(key='empty.line', exportable=False),
            w(key='x.1'),
        ]

        duplicates = text_in.find_duplicate_wordings(wordings)
        self.assertEqual({'a.0': [1, 5]}, duplicates)

        grouped_wordings = text_in.unique_wordings_overwrite(wordings)
        self.assertEqual(
                'SECTION.A a.0 SECTION.B b.0 b.1 SECTION.A a.2 empty.line x.0 empty.line x.1',
                ' '.join(w.key for w in grouped_wordings))

    def test_unique_sections(self):
        w = text_in.Wording
        wordings = [
            w(key='___'),
            w(key='SECTION.A', is_comment=True), w(key='a.0'),
            w(key='SECTION.B', is_comment=True), w(key='b.0'), w(key='b.1'),
            w(key='SECTION.C', is_comment=True),
            w(key='SECTION.A', is_comment=True), w(key='a1'),
        ]

        duplicates = text_in.find_duplicate_comment_keys(wordings)
        self.assertEqual({'SECTION.A': [1, 7]}, duplicates)

        grouped_wordings = text_in.group_wordings_by_comment_key(wordings)
        self.assertEqual('___ SECTION.A a.0 a1 SECTION.B b.0 b.1 SECTION.C',
                         ' '.join(w.key for w in grouped_wordings))

    def test_trim(self):
        w = text_in.Wording
        wordings = [
            w(key='0', translations=OrderedDict(en='hello',   fr='bonjour ')),
            w(key='1', translations=OrderedDict(en='hello\n', fr='bonjour\n\n\n')),
            w(key='2', translations=OrderedDict(en='hello',  fr=' bonjour')),
            w(key='3', translations=OrderedDict(en='\nhello', fr='\n\n\nbonjour'))
        ]

        wordings = text_in.trimmed(wordings)

        expected_translations = OrderedDict(en='hello', fr='bonjour')
        for w in wordings:
            self.assertEqual(expected_translations, w.translations)

    def test_collection_utils(self):
        range_g = (v for v in range(10))
        self.assertEquals('[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]',
                          json.dumps(range_g, cls=StreamArrayJSONEncoder))
        self.assertEquals('[]', json.dumps(range_g, cls=StreamArrayJSONEncoder))

        Foo = namedtuple_with_defaults("Foo", 'name', dict(name="bar"))

        self.assertEquals("bar", Foo().name)
        self.assertEquals("blaz", Foo('blaz').name)
        self.assertEquals("holy", Foo(name='holy').name)

        Foo = namedtuple_with_defaults("Foo", 'name', dict(name="bar"))

        self.assertEquals("bar", Foo().name)
        self.assertEquals("blaz", Foo('blaz').name)
        self.assertEquals("holy", Foo(name='holy').name)

        Foo = namedtuple_with_defaults("Foo", 'name grail', dict(name="bar"))

        self.assertEquals("bar", Foo().name)
        assert Foo().grail is None
        self.assertEquals(True, Foo('blaz', True).grail)
        self.assertEquals("holy", Foo(name='holy').name)

        Foo = namedtuple_with_defaults("Foo", 'name grail', dict(name="bar"))

        self.assertEquals("bar", Foo().name)
        assert Foo().grail is None
        self.assertEquals(True, Foo('blaz', True).grail)
        self.assertEquals("holy", Foo(name='holy').name)


if __name__ == '__main__':
    unittest.main()
