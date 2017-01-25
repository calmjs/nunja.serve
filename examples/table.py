#!/usr/bin/env python
from nunja.core import engine
from nunja.testing import model

data = model.DummyTableData([
    ['id', 'Id'],
    ['name', 'Given Name'],
], [
    ['1', 'John Smith'],
    ['2', 'Eve Adams'],
])

print("Content-Type: text/html")
print("")

body = engine.execute('nunja.molds/table', data=data.to_jsonable())
html = engine.load_mold('nunja.molds/html5').render(
    title='Example page',
    js=['/node_modules/requirejs/require.js', '/nunja.js', '/nunja/config.js'],
    body=body,
)

print(html)
