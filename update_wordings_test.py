#!/usr/bin/env python
# coding=utf-8
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
        print 'csv\n'+'\n'.join(repr(w) for w in wordings_from_csv)

        self.assertEqual(wordings_from_csv[1].key, 'menu.welcome')
        self.assertEqual(wordings_from_csv[1].translations['fr'], 'Bienvenue !')

        languages, wordings_from_xls = input.read_file('test_translations.xlsx')
        print 'xls\n'+'\n'.join(repr(w) for w in wordings_from_xls)

        languages, wordings_from_json = input.read_file('test_translations.json')
        print 'json\n'+'\n'.join(repr(w) for w in wordings_from_json)

        self.assertListEqual(wordings_from_csv, wordings_from_json)
        self.assertListEqual(wordings_from_csv, wordings_from_xls)

    def test_export(self):
        languages, wordings = input.read_file('test_translations.csv')

        output.write_android_strings(languages, wordings, 'test-out')
        output.write_ios_strings(languages, wordings, 'test-out')

        output.write_json(languages, wordings, 'test-out/wordings.json', True)

if __name__ == '__main__':
    unittest.main()
