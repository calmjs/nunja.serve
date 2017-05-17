# -*- coding: utf-8 -*-
from pkg_resources import Distribution

from calmjs.registry import _inst as default_registry
from calmjs.testing import mocks

from nunja.serve.base import BaseProvider
from nunja.registry import MoldRegistry

js_mimetypes = (
    'text/javascript', 'application/x-javascript', 'application/javascript')


class DummyProvider(BaseProvider):

    def fetch_core(self, identifier):
        return 'config:' + identifier

    def fetch_object(self, identifier):
        if 'notfound' in identifier:
            raise KeyError('notfound is not found')
        return 'object:' + identifier


def setup_test_mold_registry(testcase, name='nunja.mold'):
    def cleanup():
        default_registry.records.pop(name, None)

    working_set = mocks.WorkingSet({
        name: [
            'nunja.testing.mold = nunja.testing:mold',
        ]},
        dist=Distribution(project_name='nunja.testing')
    )
    registry = MoldRegistry(name, _working_set=working_set)
    testcase.addCleanup(cleanup)
    default_registry.records[name] = registry
