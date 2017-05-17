# -*- coding: utf-8 -*-

try:  # pragma: no cover
    import flask  # noqa: F401
    FLASK = True
except ImportError:  # pragma: no cover
    FLASK = False


if FLASK:  # pragma: no cover
    from nunja.serve.tests._test_flask import RJSProviderTestCase  # noqa: F401
