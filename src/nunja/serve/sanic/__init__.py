# -*- coding: utf-8 -*-
"""
This provide integration with sanic.

Requires Python 3.5+
"""

from sanic import response
from sanic.router import REGEX_TYPES

from nunja.serve import rjs

# Sanic 0.5.2 introduced the path type, however it also has additional
# support discerning the root parameter, so there is a bit of difference
# between the pattern we are patching for <=0.5.1.
REGEX_TYPES['path'] = REGEX_TYPES.get('path', (str, r'[^/]?.*?'))


class SanicMixin(object):
    """
    The base mixin for combining with a provider implementation.
    """

    async def serve(self, request, identifier):  # noqa: E999
        if identifier in self.core_subpaths:
            return response.text(self.fetch_core(identifier), headers={
                'Content-Type': 'application/javascript',
            })
        try:
            path = self.fetch_path(identifier)
        except KeyError:
            return response.text('404 NOT FOUND', status=404)
        return await response.file(path)

    def setup(self, app):
        """
        Set up the app with routes.
        """

        app.add_route(self.serve, self.base_url + '<identifier:path>')

    def __call__(self, app):
        self.setup(app)
        return app


class RJSProvider(SanicMixin, rjs.Provider):
    """
    Using the RJS version for serving base library stuff.

    Example usage:

    >>> from sanic import Sanic
    >>> from nunja.serve import sanic
    >>> app = sanic.RJSProvider('/nunja/')(Sanic())
    >>> app.run(port=9000)
    """
