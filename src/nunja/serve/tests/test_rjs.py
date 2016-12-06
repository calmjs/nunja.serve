# -*- coding: utf-8 -*-
import unittest

from pkg_resources import Distribution

from calmjs.registry import _inst as default_registry
from nunja.registry import MoldRegistry
from nunja.serve.rjs import make_config

from calmjs.testing import mocks
from calmjs.utils import pretty_logging


class RJSConfigTestCase(unittest.TestCase):

    def create_workingset_registry(self, name='nunja.mold'):
        working_set = mocks.WorkingSet({
            name: [
                'nunja.testing.molds = nunja.testing:mold',
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

    def test_generate_requirejs(self):
        self.setup_default()
        result = make_config('base')
        self.assertEqual(result, {
            'baseUrl': 'base',
            'paths': {
                'nunja.testing': 'nunja.mold/nunja.testing',
                'nunja.testing.molds/basic':
                    'nunja.mold/nunja.testing.molds/basic',
                'nunja.testing.molds/include_by_name':
                    'nunja.mold/nunja.testing.molds/include_by_name',
                'nunja.testing.molds/include_by_value':
                    'nunja.mold/nunja.testing.molds/include_by_value',
                'nunja.testing.molds/itemlist':
                    'nunja.mold/nunja.testing.molds/itemlist',
            }
        })

    def test_generate_requirejs_no_registry(self):
        self.setup_default()
        result = make_config('base', registries=())
        self.assertEqual(result, {'baseUrl': 'base', 'paths': {}})

    def test_generate_requirejs_bad_registry(self):
        self.setup_default()
        with pretty_logging('nunja', stream=mocks.StringIO()) as s:
            result = make_config('base', registries=('no_such_registry',))
        self.assertEqual(result, {'baseUrl': 'base', 'paths': {}})
        self.assertIn(
            "registry 'no_such_registry' does not exist", s.getvalue())

    def test_generate_requirejs_dupe_registry(self):
        self.setup_default()
        self.setup_default('nunja.mold.alt')
        with pretty_logging('nunja', stream=mocks.StringIO()) as s:
            result = make_config('base', registries=(
                'nunja.mold', 'nunja.mold.alt'))
        self.assertEqual(result, {
            'baseUrl': 'base',
            'paths': {
                'nunja.testing': 'nunja.mold.alt/nunja.testing',
                'nunja.testing.molds/basic':
                    'nunja.mold.alt/nunja.testing.molds/basic',
                'nunja.testing.molds/include_by_name':
                    'nunja.mold.alt/nunja.testing.molds/include_by_name',
                'nunja.testing.molds/include_by_value':
                    'nunja.mold.alt/nunja.testing.molds/include_by_value',
                'nunja.testing.molds/itemlist':
                    'nunja.mold.alt/nunja.testing.molds/itemlist',
            }
        })
