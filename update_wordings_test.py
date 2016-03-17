#!/usr/bin/env python
# coding=utf-8
import mobileStrings
from mobileStrings.exporters import _escape_android_string, _escape_ios_string

__author__ = 'nic'

import unittest

class MyTestCase(unittest.TestCase):

    def test_replace_tokens_android(self):
        self.assertEqual("blablabla", _escape_android_string("blablabla"))
        self.assertEqual("bla %1$s blabla", _escape_android_string("bla {} blabla"))
        self.assertEqual("bla %1$s bla %2$s bla", _escape_android_string("bla {} bla {} bla"))
        self.assertEqual("bla %1$s blabla", _escape_android_string("bla %@ blabla"))
        self.assertEqual("bla %1$s bla %2$s bla", _escape_android_string("bla %@ bla %@ bla"))

    def test_replace_tokens_ios(self):
        self.assertEqual("blablabla", _escape_ios_string("blablabla"))
        self.assertEqual("bla %@ blabla", _escape_ios_string("bla {} blabla"))
        self.assertEqual("bla %@ bla %@ bla", _escape_ios_string("bla {} bla {} bla"))
        self.assertEqual("bla %@ blabla", _escape_ios_string("bla %@ blabla"))
        self.assertEqual("bla %@ bla %@ bla", _escape_ios_string("bla %@ bla %@ bla"))

    def test_escape_android(self):
        test_string = u'< > & % \' " ’ \n \t \r \f'
        self.assertEqual(u'&lt; &gt; &amp; %% \\\' \\" \\’ \\n \\t \\r \\f', _escape_android_string(test_string))
        self.assertEqual(u'< > & % \' \\" ’ \\n \\t \\r \\f', _escape_ios_string(test_string))

    def test_import(self):
        languages, csv_wordings = mobileStrings.readers.read_file('test_translations.csv')
        print 'csv\n'+'\n'.join(repr(w) for w in csv_wordings)

        self.assertEqual(csv_wordings[1].key, 'menu.welcome')
        self.assertEqual(csv_wordings[1].translations_dict['fr'], 'Bienvenue !')

        languages, xls_wordings = mobileStrings.readers.read_file('test_translations.xlsx')
        print 'xls\n'+'\n'.join(repr(w) for w in xls_wordings)

        self.assertListEqual(csv_wordings, xls_wordings)

if __name__ == '__main__':
    unittest.main()
