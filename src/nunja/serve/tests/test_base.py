# -*- coding: utf-8 -*-
import unittest

from nunja.serve.base import BaseProvider


class DummyProvider(BaseProvider):

    def fetch_config(self, identifier):
        return 'config:' + identifier

    def fetch_object(self, identifier):
        return 'object:' + identifier


class BaseProviderTestCase(unittest.TestCase):

    def test_base_provider_construct(self):
        provider = BaseProvider('/base', config_subpaths=('config.js',))
        self.assertEqual(provider.base_url, '/base')
        self.assertEqual(provider.config_subpaths, ('config.js',))

    def test_base_provider_not_implemented(self):
        provider = BaseProvider('/base', config_subpaths=('config.js',))

        with self.assertRaises(NotImplementedError):
            provider.fetch_config('/some/path')

        with self.assertRaises(NotImplementedError):
            provider.fetch_object('/some/path')


class DummyProviderTestCase(unittest.TestCase):
    """
    For testing/formalising calling conventions for serving
    """

    def test_base_provider_serve(self):
        provider = DummyProvider('/base', config_subpaths=('config.js',))
        self.assertIsNone(provider.fetch('/elsewhere'))
        self.assertEqual(provider.fetch('/base/an_object'), 'object:an_object')
        self.assertEqual(provider.fetch('/base/config.js'), 'config:config.js')
