# -*- coding: utf-8 -*-
import unittest
import logging

from sanic import Sanic
from sanic import config

from nunja.serve.sanic import RJSProvider
from nunja.serve.testing import setup_test_mold_registry
from nunja.serve.testing import js_mimetypes

_log = logging.getLogger('sanic')


class RJSProviderTestCase(unittest.TestCase):

    def setUp(self):
        self._log_level, _log.level = _log.level, logging.CRITICAL
        self.LOGGING = {}
        if hasattr(config, 'LOGGING'):  # pragma: no cover
            self.LOGGING.update(config.LOGGING)
            config.LOGGING.clear()

        self.app = Sanic('rjs_provider_test')

    def tearDown(self):
        _log.level = self._log_level
        if hasattr(config, 'LOGGING'):  # pragma: no cover
            config.LOGGING.update(self.LOGGING)

    def test_core_config(self):
        setup_test_mold_registry(self)
        provider = RJSProvider('/nunja/')
        provider(self.app)
        request, response = self.app.test_client.get('/nunja/config.js')
        self.assertTrue(response.text.startswith(
            "(function() {\n    'use strict';\n\n"))
        self.assertIn(response.headers['Content-Type'], js_mimetypes)

    def test_core_init(self):
        provider = RJSProvider('/nunja/nested/')
        provider(self.app)
        request, response = self.app.test_client.get('/nunja/nested/init.js')
        self.assertTrue(response.text.startswith("'use strict';"))
        self.assertIn(response.headers['Content-Type'], js_mimetypes)

    def test_acquire_template(self):
        setup_test_mold_registry(self)
        provider = RJSProvider('/nunja/')
        provider(self.app)
        request, response = self.app.test_client.get(
            '/nunja/nunja.mold/nunja.testing.mold/basic/template.nja')
        self.assertEqual(response.text, '<span>{{ value }}</span>\n')

        request, response = self.app.test_client.get(
            '/nunja/nunja.mold/nunja.testing.mold/itemlist/index.js')
        self.assertIn(response.headers['Content-Type'], js_mimetypes)

    def test_acquire_missing(self):
        provider = RJSProvider('/nunja/')
        provider(self.app)
        request, response = self.app.test_client.get('/nunja/nested/init.js')
        self.assertEqual(response.status, 404)
        request, response = self.app.test_client.get(
            '/nunja/nunja.mold/nunja.testing.mold/no_such_thing/template.nja')
        self.assertEqual(response.status, 404)
        request, response = self.app.test_client.get(
            '/nunja/nunja.mold/nunja.testing.mold/basic/not_found.nja')
        self.assertEqual(response.status, 404)
