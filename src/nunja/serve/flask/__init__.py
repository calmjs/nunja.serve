# -*- coding: utf-8 -*-
"""
This provide integration with sanic.

Requires Python 3.5+
"""

import mimetypes
from flask import make_response

from nunja.serve import rjs


class FlaskMixin(object):
    """
    The base mixin for combining with a provider implementation.
    """

    def serve(self, identifier):
        mimetype = mimetypes.guess_type(identifier)[0] or 'text/plain'
        if identifier in self.core_subpaths:
            response = make_response(self.fetch_core(identifier))
        else:
            try:
                response = make_response(self.fetch_object(identifier))
            except (KeyError, OSError):
                return make_response('404 NOT FOUND', 404)

        response.headers['Content-Type'] = mimetype
        return response

    def setup(self, app):
        """
        Set up the app with routes.
        """

        app.add_url_rule(
            self.base_url + '<path:identifier>', 'nunja', self.serve)

    def __call__(self, app):
        self.setup(app)
        return app


class RJSProvider(FlaskMixin, rjs.Provider):
    """
    Using the RJS version for serving base library stuff.

    Example usage:

    >>> from flask import Flask
    >>> from nunja.serve import flask
    >>> app = flask.RJSProvider('/nunja/')(Flask(__name__))
    >>> app.run(port=9000)
    """
