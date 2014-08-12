# coding=utf-8
import os
import unittest
from application.views import make_cache_key, csv_processor


class HomepageTest(unittest.TestCase):
    def test_make_cache_key(self):
        key = make_cache_key('a', 'b')
        self.assertEqual(key, 'a_b')
        key = make_cache_key('a', '_b')
        self.assertEqual(key, 'a__b')

    def test_csv_processor(self):
        fh = open(os.path.join(os.path.abspath('.'), 'providerreport.csv'), os.O_RDONLY)
        fake_csv_data = file.read(fh, 50000)
        csv_data = csv_processor(fake_csv_data)
        print csv_data
        self.assertEqual(len(csv_data), 1)
        self.assertEqual(csv_data[0]['Provider Name'], 'Ian Douglas')
