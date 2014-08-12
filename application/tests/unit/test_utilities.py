# coding=utf-8
import unittest
from application.views import make_cache_key, csv_processor, csvstring2dict
from application.tests import PROVIDER_REPORT


class HomepageTest(unittest.TestCase):
    def test_csvstring2dict(self):
        csv_data = "column1,column2\ndata1,data2"
        csv_dict = csvstring2dict(csv_data)
        self.assertDictEqual(csv_dict[0], {'column1': 'data1', 'column2': 'data2'})

    def test_make_cache_key(self):
        key = make_cache_key('a', 'b')
        self.assertEqual(key, 'a_b')
        key = make_cache_key('a', '_b')
        self.assertEqual(key, 'a__b')

    def test_csv_processor(self):
        fake_csv_data = PROVIDER_REPORT
        csv_data = csv_processor(fake_csv_data)
        self.assertEqual(len(csv_data), 4)
        self.assertEqual(csv_data[0]['Provider Name'], 'Ian Douglas')
