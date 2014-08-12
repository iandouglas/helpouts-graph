# coding=utf-8
import unittest
from StringIO import StringIO
import flask
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
        self.test_app = self.app.test_client()
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

    def test_400(self):
        rv = self.client.get('/lkajsdlkjasd')
        self.assertTrue('404' in rv.data)

    def test_500(self):
        with self.app.test_request_context():
            self.client.get('/')

            rv = self.test_app.post(
                '/graph',
                buffered=True,
                content_type='multipart/form-data',
                data={'csv_upload':
                      (StringIO(''), 'upload.csv')})

            self.assertTrue(rv.status_code, 500)
            self.assertTrue('Ruh-roh, something goofed up.' in rv.data)
