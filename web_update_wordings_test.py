#!/usr/bin/env python
# coding=utf-8
from collections import namedtuple

import web_update_wordings

import unittest

web_update_wordings.cliargs = namedtuple('CliArgs', 'input_file')("./test_translations.csv")

class WebUpdateWordingsTestCase(unittest.TestCase):
    def setUp(self):
        web_update_wordings.app.config['TESTING'] = True
        self.app = web_update_wordings.app.test_client()

    def tearDown(self):
        pass

    def test_result(self):
        rv = self.app.get('/table')
        assert 'menu.welcome' in rv.data

if __name__ == '__main__':
    unittest.main()
