# coding=utf-8
import os
import unittest
import flask
from google.appengine.api import memcache
from google.appengine.ext import testbed
import time
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

    def test_graphpage_nocsvdata(self):
        self.client.get('/')
        rv = self.client.get('/graph')
        self.assertEqual(rv.status, '200 OK')
        self.assertTrue('No data to graph, sorry.' in rv.data)

    def test_graphpage_fakecsvdata(self):
        with self.app.test_request_context():
            self.client.get('/')
            flask.session['sid'] = int(time.time())
            sid = flask.session['sid']
            fake_csv_fh = os.open(os.path.join(os.path.abspath('.'), 'providerreport.csv'), os.O_RDONLY)
            fake_csv_data = os.read(fake_csv_fh, 50000)
            memcache.set(str(sid), fake_csv_data, 600)
            rv = self.client.get('/graph')
            self.assertEqual(rv.status, '200 OK')
            self.assertFalse('No data to graph, sorry.' in rv.data)
