# -*- coding: utf-8 -*-
"""
Compatibility imports between Python 2 and 3.
"""

import sys

if sys.version_info > (3,):  # pragma: no cover
    from http.server import HTTPServer
    from http.server import SimpleHTTPRequestHandler
    from http.server import CGIHTTPRequestHandler
    from http.client import HTTPConnection
else:  # pragma: no cover
    from BaseHTTPServer import HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from CGIHTTPServer import CGIHTTPRequestHandler
    from httplib import HTTPConnection

__all__ = [
    'HTTPServer', 'CGIHTTPRequestHandler', 'SimpleHTTPRequestHandler',
    'HTTPConnection',
]
