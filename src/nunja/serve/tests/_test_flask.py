# -*- coding: utf-8 -*-
import unittest

from flask import Flask

from nunja.serve.flask import RJSProvider
from nunja.serve.testing import setup_test_mold_registry
from nunja.serve.testing import js_mimetypes


class RJSProviderTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask('rjs_provider_test')
        self.test_client = self.app.test_client()

    def tearDown(self):
        pass

    def test_core_config(self):
        setup_test_mold_registry(self)
        provider = RJSProvider('/nunja/')
        provider(self.app)
        rv = self.test_client.get('/nunja/config.js')
        self.assertIn(rv.headers['Content-Type'], js_mimetypes)
        self.assertTrue(rv.data.startswith(
            b"(function() {\n    'use strict';\n\n"))

    def test_core_init(self):
        provider = RJSProvider('/nunja/nested/')
        provider(self.app)
        rv = self.test_client.get('/nunja/nested/init.js')
        self.assertIn(rv.headers['Content-Type'], js_mimetypes)
        self.assertTrue(rv.data.startswith(b"'use strict';"))

    def test_acquire_template(self):
        setup_test_mold_registry(self)
        provider = RJSProvider('/nunja/')
        provider(self.app)
        rv = self.test_client.get(
            '/nunja/nunja.mold/nunja.testing.mold/basic/template.nja')
        self.assertEqual(rv.data, b'<span>{{ value }}</span>\n')

        rv = self.test_client.get(
            '/nunja/nunja.mold/nunja.testing.mold/itemlist/index.js')
        self.assertIn(rv.headers['Content-Type'], js_mimetypes)

    def test_acquire_missing(self):
        provider = RJSProvider('/nunja/')
        provider(self.app)
        rv = self.test_client.get('/nunja/nested/init.js')
        self.assertEqual(rv.status_code, 404)
        rv = self.test_client.get(
            '/nunja/nunja.mold/nunja.testing.mold/no_such_thing/template.nja')
        self.assertEqual(rv.status_code, 404)
        rv = self.test_client.get(
            '/nunja/nunja.mold/nunja.testing.mold/basic/not_found.nja')
        self.assertEqual(rv.status_code, 404)
