# -*- coding: utf-8 -*-
"""
The simple server is built on top of the builtin server and request
handler classes from the standard library.  This can simply be invoked
in a directory that provide some static templates that has hooks into
the JavaScript nunja libraries.

Alternatively, server side rendering can be enabled for Python scripts;
if the option is set, Python scripts will be executed for the generation
of templates.
"""

import sys
from io import BytesIO
import posixpath

from nunja.registry import ENTRY_POINT_NAME
from nunja.serve.compat import HTTPServer
from nunja.serve.compat import CGIHTTPRequestHandler


def normpath(path):
    return posixpath.normpath('/' + path)


class NunjaHTTPRequestHandler(CGIHTTPRequestHandler):
    """
    Same as simple HTTP request heandler for serving local files, but
    specific paths can be specified to be proxies for specific external
    content to get around cross-site origin restrictions.
    """

    def __init__(
            self, request, client_address, server,
            nunja_prefix, provider):
        """
        In addition to the request, client_address and server arguments,
        nunja also need to know the prefix, have an instance of the js
        provider.
        """
        self.nunja_prefix = nunja_prefix
        self.provider = provider
        CGIHTTPRequestHandler.__init__(
            self, request, client_address, server)

    def is_cgi(self):
        """
        Doing the somewhat dangerous thing of permitting _any_ Python
        scripts found.
        """

        self.path = normpath(self.path)
        if self.path.endswith('.py'):
            self.cgi_info = self.path.rsplit('/', 1)
            return True
        return CGIHTTPRequestHandler.is_cgi(self)

    def send_head(self):
        if not self.path.startswith(self.nunja_prefix + '/'):
            return CGIHTTPRequestHandler.send_head(self)
            # TODO maybe have an option to merge the two "trees"?

        try:
            text = self.provider.fetch(self.path)
        except KeyError:
            text = '404 NOT FOUND'
            self.send_response(404)
            self.send_header("Content-type", 'text/plain')
        else:
            self.send_response(200)
            # XXX fix headers
            self.send_header("Content-type", 'text/plain')

        self.send_header("Content-Length", str(len(text)))
        self.end_headers()
        return BytesIO(text.encode('utf8'))


class NunjaHTTPRequestHandlerFactory(object):
    """
    Produces a handler constructor that will assign attributes that the
    handler implementation will need.
    """

    def __init__(
            self, provider,
            nunja_prefix='/nunja', registry_names=(ENTRY_POINT_NAME,),
            handler_cls=NunjaHTTPRequestHandler,
            ):
        """
        Parameters

        nunja_prefix
            The path prefix that will be served by the registry.  It
            must start with a '/'.
        registry_names
            The names of registries.  Defaults to just nunja.mold
        """

        self.nunja_prefix = nunja_prefix
        self.provider = provider
        self.handler_cls = handler_cls

    def __call__(self, request, client_address, server):
        cls = self.handler_cls(
            request, client_address, server, self.nunja_prefix, self.provider)
        return cls


def serve_nunja(
        provider_cls,
        server=None,
        server_factory=HTTPServer,
        handler_cls=NunjaHTTPRequestHandler,
        nunja_prefix='/nunja',
        registry_names=(ENTRY_POINT_NAME,),
        bind='',
        port=8000,
        protocol="HTTP/1.0",
        ):
    """
    Simple requirejs based server.
    """

    # TODO should the config_subpath be configurable?
    provider = provider_cls(nunja_prefix, registry_names=registry_names)
    addr = (bind, port)
    handler = NunjaHTTPRequestHandlerFactory(
        provider,
        handler_cls=handler_cls,
        nunja_prefix=nunja_prefix,
        registry_names=registry_names,
    )
    if server is None:
        server = server_factory(addr, handler)
    sa = server.socket.getsockname()
    print('Serving HTTP on %s:%s...' % sa)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nKeyboard interrupt received, shutting down...')
        server.server_close()
        sys.exit(0)


def main(provider_cls):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', '-b', default='127.0.0.1', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]')
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    args = parser.parse_args()
    serve_nunja(provider_cls=provider_cls, port=args.port, bind=args.bind)
