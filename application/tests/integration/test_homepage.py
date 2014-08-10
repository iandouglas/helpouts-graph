# coding=utf-8
from splinter import Browser
import unittest
from google.appengine.ext import testbed

browser = Browser()


class HomepageTest(unittest.TestCase):
    def setUp(self):
        global browser
        self.tb = testbed.Testbed()
        self.tb.activate()
        self.tb.init_memcache_stub()

    def tearDown(self):
        self.tb.deactivate()

    def test_splinter_homepage(self):
        browser.visit('http://127.0.0.1:8080/')
        self.assertEqual(browser.is_text_present('You will need to be logged in on the same Google account'), True)

    def test_splinter_homepage_nocsv(self):
        browser.visit('http://127.0.0.1:8080/')
        self.assertEqual(browser.is_text_present('You will need to be logged in on the same Google account'), True)
        browser.find_by_id('submit').click()
        self.assertEqual(browser.is_text_present('No data to graph, sorry'), True)

    def test_splinter_homepage_withcsv(self):
        browser.visit('http://127.0.0.1:8080/')
        self.assertEqual(browser.is_text_present('You will need to be logged in on the same Google account'), True)
        browser.attach_file('csv_upload', 'providerreport.csv')
        self.assertEqual(browser.is_text_present('No data to graph, sorry'), False)

    def test_zzzzz_last_test(self):
        browser.quit()
