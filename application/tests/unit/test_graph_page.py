# coding=utf-8
import unittest
from StringIO import StringIO
import flask
from google.appengine.api import memcache
from google.appengine.ext import testbed
import time
from application import create_app
from application.routes import create_routes
from application.views import make_cache_key
from application.tests import PROVIDER_REPORT


class HomepageTest(unittest.TestCase):
    def setUp(self):
        self.tb = testbed.Testbed()
        self.tb.activate()
        self.tb.init_memcache_stub()

        self.app = create_app()
        self.test_app = self.app.test_client()
        self.app.debug = True
        create_routes(self.app)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        self.tb.deactivate()

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
            fake_csv_data = PROVIDER_REPORT
            memcache.set(make_cache_key(str(sid), 'raw'), fake_csv_data, 600)
            rv = self.client.get('/graph')
            self.assertFalse('No data to graph, sorry.' in rv.data)

    def test_graphpage_upload(self):
        with self.app.test_request_context():
            self.client.get('/')
            flask.session['sid'] = int(time.time())

            self.test_app.post(
                '/graph',
                buffered=True,
                content_type='multipart/form-data',
                data={'csv_upload':
                      (StringIO(PROVIDER_REPORT), 'upload.csv')})

            rv = self.client.get('/graph/SUCCESSFUL')
            self.assertEqual(rv.status, '200 OK')
            self.assertFalse('No data to graph, sorry.' in rv.data)
            self.assertFalse('Your session has ended' in rv.data)

    def test_graphpage_state(self):
        with self.app.test_request_context():
            self.client.get('/')
            flask.session['sid'] = int(time.time())
            sid = flask.session['sid']
            fake_csv_data = PROVIDER_REPORT
            memcache.set(make_cache_key(str(sid), 'raw'), fake_csv_data, 600)
            rv = self.client.get('/graph/SUCCESSFUL')
            self.assertEqual(rv.status, '200 OK')
            self.assertFalse('No data to graph, sorry.' in rv.data)
            self.assertFalse('Your session has ended' in rv.data)

            rv = self.client.get('/graph/UNSUCCESSFUL')
            self.assertFalse('No data to graph, sorry.' in rv.data)
            self.assertFalse('Your session has ended' in rv.data)

            rv = self.client.get('/graph/FUTURE')
            self.assertFalse('No data to graph, sorry.' in rv.data)
            self.assertFalse('Your session has ended' in rv.data)

            rv = self.client.get('/graph/CANCELLED')
            self.assertFalse('No data to graph, sorry.' in rv.data)
            self.assertFalse('Your session has ended' in rv.data)

            memcache.set(make_cache_key(str(sid), 'raw'), '', 600)
            rv = self.client.get('/graph/SUCCESSFUL')
            self.assertTrue('Your session has ended' in rv.data)
