# -*- coding: utf-8 -*-
"""
This provide integration with sanic.

Requires Python 3.5+
"""

from sanic import response

from nunja.serve import rjs


class SanicMixin(object):
    """
    The base mixin for combining with a provider implementation.
    """

    async def serve(self, request, identifier):  # noqa: E999
        if identifier in self.core_subpaths:
            return response.text(self.fetch_core(identifier))
        try:
            path = self.fetch_path(identifier)
        except KeyError:
            return response.text('404 NOT FOUND', status=404)
        return await response.file(path)

    def setup(self, app):
        """
        Set up the app with routes.
        """

        app.add_route(self.serve, self.base_url + '<identifier:.*>')

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
