# -*- coding: utf-8 -*-
from nunja.serve.base import BaseProvider


class DummyProvider(BaseProvider):

    def fetch_core(self, identifier):
        return 'config:' + identifier

    def fetch_object(self, identifier):
        if 'notfound' in identifier:
            raise KeyError('notfound is not found')
        return 'object:' + identifier
