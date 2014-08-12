# coding=utf-8
import unittest
from google.appengine.ext import testbed
from application import create_app
from application.routes import create_routes


class HomepageTest(unittest.TestCase):
    def setUp(self):
        self.tb = testbed.Testbed()
        self.tb.activate()
        self.tb.init_memcache_stub()

        self.app = create_app()
        self.app.debug = True
        create_routes(self.app)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        self.tb.deactivate()

    def test_warmup(self):
        rv = self.client.get('/_ah/warmup')
        self.assertEqual(rv.status, '200 OK')
        self.assertEqual('', rv.data)

    def test_homepage(self):
        rv = self.client.get('/')
        self.assertEqual(rv.status, '200 OK')
        self.assertTrue('You will need to be logged in on the same Google account' in rv.data)

    def test_google_analytics(self):
        rv = self.client.get('/')
        self.assertTrue('UA-142829-32' in rv.data)
        rv = self.client.get('/graph')
        self.assertTrue('UA-142829-32' in rv.data)
