# -*- coding: utf-8 -*-
import unittest
import os
import sys
import threading

from calmjs.testing.utils import mkdtemp
from calmjs.testing.utils import stub_item_attr_value
from calmjs.testing.utils import stub_stdouts
from calmjs.testing.utils import remember_cwd

from nunja.serve.compat import HTTPServer
from nunja.serve.compat import HTTPConnection

from nunja.serve import simple
# from nunja.serve.simple import NunjaHTTPRequestHandler
from nunja.serve.simple import NunjaHTTPRequestHandlerFactory
from nunja.serve.simple import _is_cgi
from nunja.serve.simple import normpath
from nunja.serve.simple import main
from nunja.serve.simple import serve_nunja
from nunja.serve.testing import DummyProvider


def base_setup(inst):
    stub_stdouts(inst)
    remember_cwd(inst)
    tmpdir = mkdtemp(inst)
    os.chdir(tmpdir)
    with open(os.path.join(tmpdir, 'file.txt'), 'w') as fd:
        fd.write('hello')

    with open(os.path.join(tmpdir, 'script.py'), 'w') as fd:
        fd.write('#!/usr/bin/env python\n')
        fd.write('print("Content-Type: text/html")\n')
        fd.write('print("")\n')
        fd.write('print("Hello World")\n')
    os.chmod(os.path.join(tmpdir, 'script.py'), 0o777)

    with open(os.path.join(tmpdir, 'header.py'), 'w') as fd:
        fd.write('#!/usr/bin/env python\n')
        fd.write('import os\n')
        fd.write('print("Content-Type: text/plain")\n')
        fd.write('print("")\n')
        fd.write('print(os.environ["HTTP_ACCEPT"])\n')
    os.chmod(os.path.join(tmpdir, 'header.py'), 0o777)

    os.mkdir(os.path.join(tmpdir, 'dir'))


class SupportTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_normpath(self):
        self.assertEqual(normpath('/'), '/')
        self.assertEqual(normpath('/some//where'), '/some/where')
        self.assertEqual(normpath('/somewhere/'), '/somewhere/')

    def test_is_cgi_filename(self):
        result, path, query = _is_cgi('/somewhere/path.txt')
        self.assertFalse(result)
        self.assertEqual('/somewhere/path.txt', path)
        self.assertEqual(query, '')

    def test_is_cgi_python_not_exists(self):
        result, path, query = _is_cgi('/nowhere/path.py')
        self.assertFalse(result)
        self.assertEqual('/nowhere/path.py', path)
        self.assertEqual(query, '')

    def test_is_cgi_python_exists(self):
        remember_cwd(self)
        tmpdir = mkdtemp(self)
        os.chdir(tmpdir)
        with open(os.path.join(tmpdir, 'script.py'), 'w') as fd:
            fd.write('print("hello")')

        result, path, query = _is_cgi('script.py')
        self.assertTrue(result)
        self.assertEqual('script.py', path)
        self.assertEqual(query, '')

    def test_is_cgi_query(self):
        remember_cwd(self)
        tmpdir = mkdtemp(self)
        os.chdir(tmpdir)
        workdir = os.path.join(tmpdir, 'some', 'nested')
        os.makedirs(os.path.join(workdir))
        fn = os.path.join(workdir, 'script.py')
        with open(fn, 'w') as fd:
            fd.write('print("hello")')

        result, path, query = _is_cgi('/some/nested/script.py?some_argument')
        self.assertTrue(result)
        self.assertEqual('/some/nested/script.py', path)
        self.assertEqual(query, 'some_argument')

        result, path, query = _is_cgi('/some/nested/script.py?path/argument')
        self.assertTrue(result)
        self.assertEqual('/some/nested/script.py', path)
        self.assertEqual(query, 'path/argument')


class RequestHandlerTestCase(unittest.TestCase):

    def setUp(self):
        base_setup(self)
        dummy = DummyProvider('/base', config_subpaths=('config.js',))
        handler = NunjaHTTPRequestHandlerFactory(dummy, nunja_prefix='/base')
        self.server = HTTPServer(('localhost', 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.host, self.port = self.server.socket.getsockname()
        self.thread.start()

    def tearDown(self):
        self.server.server_close()
        self.server.shutdown()

    def getresponse(self, url, headers={}):
        conn = HTTPConnection(self.host, self.port)
        conn.request('GET', url, headers=headers)
        return conn.getresponse()

    def getresponse_text(self, url, headers={}):
        return self.getresponse(url, headers).read().decode('utf8').strip()

    def test_request_handler_fallback(self):
        self.assertEqual(self.getresponse('/file.txt').read(), b'hello')
        self.assertEqual(self.getresponse('/notfound').status, 404)

    def test_directory_render(self):
        # Ensure that this wasn't accidentally broken.
        results = self.getresponse_text('/')
        self.assertIn('file.txt', results)
        self.assertIn('script.py', results)
        results = self.getresponse_text('/dir/')
        self.assertIn('/dir/', results)

    def test_request_handler_basic(self):
        self.assertEqual(
            self.getresponse_text('/base/an_object'), 'object:an_object')
        self.assertEqual(
            self.getresponse_text('/base/config.js'), 'config:config.js')

    def test_request_handler_cgi(self):
        self.assertEqual(
            'Hello World', self.getresponse_text('/script.py'))
        self.assertEqual(
            'Hello World', self.getresponse_text('/script.py?/hello'))

    def test_request_handler_cgi_http_accept(self):
        self.assertEqual('', self.getresponse_text('/header.py', {}))
        self.assertEqual(
            'application/json', self.getresponse_text('/header.py?', {
                b'Accept': b'application/json',
            }))

    def test_request_handler_notfound(self):
        self.assertEqual(self.getresponse('/base/notfound').status, 404)


class NeuteredServer(HTTPServer):

    def serve_forever(self):
        raise KeyboardInterrupt  # cheater


class ServeNunjaTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_server_flow_basic(self):
        base_setup(self)
        with self.assertRaises(SystemExit):
            serve_nunja(DummyProvider, server_factory=NeuteredServer, port=0)
        stdout = sys.stdout.getvalue()
        self.assertIn('Serving HTTP on', stdout)
        self.assertIn('Keyboard interrupt received, shutting down...', stdout)

    def test_main(self):
        stub_item_attr_value(self, sys, 'argv', ['script'])
        values = {}

        def fake_serve_nunja(**kw):
            values.update(kw)

        stub_item_attr_value(self, simple, 'serve_nunja', fake_serve_nunja)
        main(DummyProvider)

        self.assertEqual(values['port'], 8000)
        self.assertEqual(values['bind'], '127.0.0.1')
        self.assertEqual(values['provider_cls'], DummyProvider)

    # This test can't be stopped...
    # def test_server_flow_handling(self):
    #     thread = threading.Thread(target=serve_nunja, kwargs={
    #         'provider_cls': DummyProvider,
    #         'handler_cls': NunjaHTTPRequestHandler,
    #         'config_subpaths': ('my_config.js',),
    #         'port': 8000,
    #     })
    #     thread.start()
    #     conn = HTTPConnection('localhost', 8000)
    #     conn.request('GET', '/nunja/my_config.js')
    #     response = conn.getresponse()
    #     self.assertEqual(response.read(), b'config:my_config.js')
