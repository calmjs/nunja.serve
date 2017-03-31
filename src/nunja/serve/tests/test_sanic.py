# -*- coding: utf-8 -*-
import sys

try:  # pragma: no cover
    import sanic  # noqa: F401
    # also ensure we have the minimum python version for Sanic to work
    SANIC = sys.version_info > (3, 5)
except (SyntaxError, ImportError):  # pragma: no cover
    SANIC = False


if SANIC:  # pragma: no cover
    from nunja.serve.tests._test_sanic import RJSProviderTestCase  # noqa: F401
