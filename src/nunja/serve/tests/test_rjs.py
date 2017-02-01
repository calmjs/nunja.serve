# -*- coding: utf-8 -*-
import unittest
import json

from pkg_resources import Distribution

from calmjs.registry import _inst as default_registry
from calmjs.rjs.ecma import parse

from nunja.registry import MoldRegistry

from nunja.serve.rjs import Provider
from nunja.serve.rjs import fetch
from nunja.serve.rjs import make_config

from calmjs.testing import mocks
from calmjs.utils import pretty_logging


class BaseTestCase(unittest.TestCase):

    def create_workingset_registry(self, name='nunja.mold'):
        working_set = mocks.WorkingSet({
            name: [
                'nunja.testing.mold = nunja.testing:mold',
            ]},
            dist=Distribution(project_name='nunja.testing')
        )
        registry = MoldRegistry(name, _working_set=working_set)
        return working_set, registry

    def setup_default(self, name='nunja.mold'):
        def cleanup():
            default_registry.records.pop(name, None)

        working_set, registry = self.create_workingset_registry(name)
        self.addCleanup(cleanup)
        default_registry.records[name] = registry


class RJSConfigTestCase(BaseTestCase):

    def test_generate_requirejs(self):
        self.setup_default()
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
        self.setup_default()
        result = make_config('base', registry_names=())
        self.assertEqual(result, {'baseUrl': 'base', 'paths': {}})

    def test_generate_requirejs_bad_registry(self):
        self.setup_default()
        with pretty_logging('nunja', stream=mocks.StringIO()) as s:
            result = make_config('base', registry_names=('no_such_registry',))
        self.assertEqual(result, {'baseUrl': 'base', 'paths': {}})
        self.assertIn(
            "registry 'no_such_registry' does not exist", s.getvalue())

    def test_generate_requirejs_dupe_registry(self):
        self.setup_default()
        self.setup_default('nunja.mold.alt')
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

    def test_fetch_missing_registry(self):
        self.setup_default()
        # force a missing
        default_registry.records['nunja.mold'] = None
        with self.assertRaises(KeyError):
            fetch('nunja.mold', 'nunja.testing.mold/basic/template.nja')

    def test_fetch_missing_target(self):
        self.setup_default()
        with self.assertRaises(KeyError):
            fetch('nunja.mold', 'nunja.testing.mold/basic/not_found')

    def test_fetch_good(self):
        self.setup_default()
        result = fetch('nunja.mold', 'nunja.testing.mold/basic/template.nja')
        self.assertEqual(result, '<span>{{ value }}</span>\n')


class ProviderTestCase(BaseTestCase):

    def test_fetch_config(self):
        self.setup_default()
        server = Provider('base')
        result = server.fetch_config('base/config.js')

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
        self.setup_default()
        server = Provider('base')
        with self.assertRaises(KeyError):
            server.fetch_object('nunja.mold')

    def test_fetch_object_disabled_registry(self):
        self.setup_default()
        server = Provider('base', registry_names=())
        with self.assertRaises(KeyError):
            server.fetch_object(
                'nunja.mold/nunja.testing.mold/basic/template.nja')

    def test_fetch_object_good(self):
        self.setup_default()
        server = Provider('base')
        result = server.fetch_object(
            'nunja.mold/nunja.testing.mold/basic/template.nja')
        self.assertEqual(result, '<span>{{ value }}</span>\n')
