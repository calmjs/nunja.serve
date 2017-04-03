# -*- coding: utf-8 -*-
import unittest
from os.path import join

from nunja.serve.base import BaseProvider
from nunja.serve.base import fetch

from calmjs.testing.utils import mkdtemp
from nunja.serve.testing import DummyProvider


class BaseProviderTestCase(unittest.TestCase):

    def test_base_provider_empty(self):
        provider = BaseProvider('/base/', core_subpaths=())
        self.assertEqual(provider.base_url, '/base/')
        self.assertEqual(provider.core_subpaths, set())
        self.assertEqual(set(provider.yield_core_paths()), set())

    def test_base_provider_construct(self):
        provider = BaseProvider('/base/', core_subpaths=('config.js',))
        self.assertEqual(provider.base_url, '/base/')
        self.assertEqual(provider.core_subpaths, {'config.js'})
        self.assertEqual(set(provider.yield_core_paths()), {'/base/config.js'})

    def test_base_provider_not_implemented(self):
        provider = BaseProvider('/base', core_subpaths=('config.js',))

        with self.assertRaises(NotImplementedError):
            provider.fetch_core('/some/path')

        with self.assertRaises(NotImplementedError):
            provider.fetch_object('/some/path')


class DummyProviderTestCase(unittest.TestCase):
    """
    For testing/formalising calling conventions for serving
    """

    def test_base_provider_serve(self):
        provider = DummyProvider('/base/', core_subpaths=('config.js',))
        self.assertIsNone(provider.fetch('/elsewhere'))
        self.assertEqual(provider.fetch('/base/an_object'), 'object:an_object')
        self.assertEqual(provider.fetch('/base/config.js'), 'config:config.js')

    def test_base_provider_serve_errors(self):
        provider = DummyProvider('/base/', core_subpaths=('config.js',))
        with self.assertRaises(KeyError):
            provider.fetch('/base/notfound')

    def test_get_path_fetch_good(self):
        p = join(mkdtemp(self), 'file')
        with open(p, 'w') as fd:
            fd.write('hello')
        result = fetch(p)
        self.assertEqual(result, 'hello')
