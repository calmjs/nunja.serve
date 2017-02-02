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
import posixpath
from io import BytesIO
from os import getcwd
from os.path import exists
from os.path import join
from types import MethodType

from nunja.registry import ENTRY_POINT_NAME
from nunja.serve.compat import HTTPServer
from nunja.serve.compat import CGIHTTPRequestHandler


def normpath(path):
    ending = '/' if path[1:].endswith('/') else ''
    return posixpath.normpath('/' + path).replace('//', '/') + ending


def _is_cgi(path):
    """
    Locate an available python script from the path and pass on all
    remaining fragments to the script.
    """

    query = ''

    # Original plan was to pass the extra paths after the script as a
    # parameter (for use case such as url templates), but to support this
    # for the default server looks to be difficult.
    #
    # for frag in frags:
    #     q = frag.find('?')
    #     if q >= 0:
    #         resolved.append(frag[:q])
    #         # XXX there is a chunk that is truncated.
    #         query = path.split('?', 1)[1]
    #         break
    #     resolved.append(frag)

    resolved = path.split('?')[0].split('/')
    if path.find('?') >= 0:
        query = path.split('?', 1)[1]

    translated = join(getcwd(), *resolved)
    if translated.endswith('.py') and exists(translated):
        return True, '/'.join(resolved), query
    return False, '/'.join(resolved), query


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

        # Hotfix broken function that breaks HTTP_ACCEPT
        #
        # TODO whenever upstream fixes this (never?) verify that this
        # will not break that new version.  Related issues:
        #
        #     - http://bugs.python.org/issue5053
        #     - http://bugs.python.org/issue5054

        def getallmatchingheaders(self, name):
            if name in self:
                return [name + ':' + self.get(name)]
            else:
                return []

        self.headers.getallmatchingheaders = MethodType(
            getallmatchingheaders, self.headers)

        self.path = normpath(self.path)
        status, path, query = _is_cgi(self.path)

        if status:
            self.path = path
            self.cgi_info = path.rsplit('/', 1)
            # restore the query
            self.cgi_info[1] = self.cgi_info[1] + '?' + query
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
