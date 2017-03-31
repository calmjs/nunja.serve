# -*- coding: utf-8 -*-
import unittest
import json

from calmjs.registry import _inst as default_registry
from calmjs.rjs.ecma import parse

from nunja.serve.rjs import Provider
from nunja.serve.rjs import get_path
from nunja.serve.rjs import make_config

from calmjs.testing import mocks
from calmjs.utils import pretty_logging

from nunja.serve.testing import setup_test_mold_registry


class RJSConfigTestCase(unittest.TestCase):

    def test_generate_requirejs(self):
        setup_test_mold_registry(self)
        result = make_config('base')
        self.assertEqual(result, {
            'baseUrl': 'base',
            'paths': {
                'nunja.testing': 'nunja.mold/nunja.testing',
                'nunja.testing.mold/basic':
                    'nunja.mold/nunja.testing.mold/basic',
                'nunja.testing.mold/include_by_name':
                    'nunja.mold/nunja.testing.mold/include_by_name',
                'nunja.testing.mold/include_by_value':
                    'nunja.mold/nunja.testing.mold/include_by_value',
                'nunja.testing.mold/itemlist':
                    'nunja.mold/nunja.testing.mold/itemlist',
                'nunja.testing.mold/noinit':
                    'nunja.mold/nunja.testing.mold/noinit',
                'nunja.testing.mold/problem':
                    'nunja.mold/nunja.testing.mold/problem',
            }
        })

    def test_generate_requirejs_no_registry(self):
        setup_test_mold_registry(self)
        result = make_config('base', registry_names=())
        self.assertEqual(result, {'baseUrl': 'base', 'paths': {}})

    def test_generate_requirejs_bad_registry(self):
        setup_test_mold_registry(self)
        with pretty_logging('nunja', stream=mocks.StringIO()) as s:
            result = make_config('base', registry_names=('no_such_registry',))
        self.assertEqual(result, {'baseUrl': 'base', 'paths': {}})
        self.assertIn(
            "registry 'no_such_registry' does not exist", s.getvalue())

    def test_generate_requirejs_dupe_registry(self):
        setup_test_mold_registry(self)
        setup_test_mold_registry(self, 'nunja.mold.alt')
        with pretty_logging('nunja', stream=mocks.StringIO()):
            result = make_config('base', registry_names=(
                'nunja.mold', 'nunja.mold.alt'))
        self.assertEqual(result, {
            'baseUrl': 'base',
            'paths': {
                'nunja.testing': 'nunja.mold.alt/nunja.testing',
                'nunja.testing.mold/basic':
                    'nunja.mold.alt/nunja.testing.mold/basic',
                'nunja.testing.mold/include_by_name':
                    'nunja.mold.alt/nunja.testing.mold/include_by_name',
                'nunja.testing.mold/include_by_value':
                    'nunja.mold.alt/nunja.testing.mold/include_by_value',
                'nunja.testing.mold/itemlist':
                    'nunja.mold.alt/nunja.testing.mold/itemlist',
                'nunja.testing.mold/noinit':
                    'nunja.mold.alt/nunja.testing.mold/noinit',
                'nunja.testing.mold/problem':
                    'nunja.mold.alt/nunja.testing.mold/problem',
            }
        })

    def test_get_path_missing_registry(self):
        setup_test_mold_registry(self)
        # force a missing
        default_registry.records['nunja.mold'] = None
        with self.assertRaises(KeyError):
            get_path('nunja.mold', 'nunja.testing.mold/basic/template.nja')

    def test_get_path_missing_target(self):
        setup_test_mold_registry(self)
        with self.assertRaises(KeyError):
            get_path('nunja.mold', 'nunja.testing.mold/basic/not_found')


class ProviderTestCase(unittest.TestCase):

    def test_fetch_core_init(self):
        setup_test_mold_registry(self)
        server = Provider('base')
        result = server.fetch_core('init.js')
        self.assertTrue(result.startswith("'use strict'"))

    def test_fetch_core_config(self):
        setup_test_mold_registry(self)
        server = Provider('base')
        result = server.fetch_core('config.js')

        tree = parse(result)
        config = json.loads(tree.children()[0].children()[0].children()[
            0].children()[2].children()[0].children()[1].to_ecma())

        self.assertEqual(config, {
            'baseUrl': 'base',
            'paths': {
                'nunja.testing': 'nunja.mold/nunja.testing',
                'nunja.testing.mold/basic':
                    'nunja.mold/nunja.testing.mold/basic',
                'nunja.testing.mold/include_by_name':
                    'nunja.mold/nunja.testing.mold/include_by_name',
                'nunja.testing.mold/include_by_value':
                    'nunja.mold/nunja.testing.mold/include_by_value',
                'nunja.testing.mold/itemlist':
                    'nunja.mold/nunja.testing.mold/itemlist',
                'nunja.testing.mold/noinit':
                    'nunja.mold/nunja.testing.mold/noinit',
                'nunja.testing.mold/problem':
                    'nunja.mold/nunja.testing.mold/problem',
            }
        })

    def test_fetch_object_insufficient_path(self):
        setup_test_mold_registry(self)
        server = Provider('base')
        with self.assertRaises(KeyError):
            server.fetch_object('nunja.mold')

    def test_fetch_object_disabled_registry(self):
        setup_test_mold_registry(self)
        server = Provider('base', registry_names=())
        with self.assertRaises(KeyError):
            server.fetch_object(
                'nunja.mold/nunja.testing.mold/basic/template.nja')

    def test_fetch_object_good(self):
        setup_test_mold_registry(self)
        server = Provider('base')
        result = server.fetch_object(
            'nunja.mold/nunja.testing.mold/basic/template.nja')
        self.assertEqual(result, '<span>{{ value }}</span>\n')
