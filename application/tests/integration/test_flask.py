# coding=utf-8
import unittest
from google.appengine.ext import testbed
from application import create_app
from application.routes import create_routes


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.tb = testbed.Testbed()
        self.tb.activate()
        self.tb.init_memcache_stub()
        self.tb.init_urlfetch_stub()

        self.app = create_app()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        self.tb.deactivate()

    def test_flask(self):
        self.assertIsNotNone(self.app)

    def test_routes(self):
        create_routes(self.app)
        self.assertIsNotNone(self.app.url_map)
        rule_count = 0
        for _ in self.app.url_map.iter_rules():
            rule_count += 1
        self.assertGreater(rule_count, 4)

