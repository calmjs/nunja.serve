Simple CGI examples
===================

This directory contain examples that can be executed to demonstrate
basic server side rendering of nunja templates.  To use with the simple
server provided via ``nunja.serve.rjs``, make a copy of the following
directory and instantiate the environment.  Assuming all required
packages have been installed (with its virtual environment active, if
any), the following commands should start a working demo server:

.. code:: sh

    $ cp -r examples /tmp/examples
    $ cd /tmp/examples
    $ calmjs npm --install nunja
    $ calmjs rjs nunja --source-registry=calmjs.module
    $ python -m nunja.serve.simple.rjs

Then point the browser to ``http://localhost:8000/table.py`` and a table
should be rendered.

The ``calmjs rjs`` command explicitly specifies the ``calmjs.module`` to
ensure no raw template strings are precompiled into the ``nunja.js``
artifact file; this then permits hot-reloading of templates with every
request to aid in development of nunja molds.
