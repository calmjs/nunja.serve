# -*- coding: utf-8 -*-
"""
Demo serving implementation based on the requirejs backed module system
and plugin for serving/retrieving template.

The goal is to provide a live-reloading server implementation for usage
during the development phase of a given library.
"""

import codecs
import json
import logging

from calmjs.utils import json_dumps
from calmjs.registry import get
from calmjs.rjs.umdjs import UMD_REQUIREJS_JSON_EXPORT_HEADER
from calmjs.rjs.umdjs import UMD_REQUIREJS_JSON_EXPORT_FOOTER
from nunja.registry import ENTRY_POINT_NAME

logger = logging.getLogger(__name__)


def make_config(base_url, registries=(ENTRY_POINT_NAME,)):
    """
    Return a configuration for requirejs to function against some end
    point.

    Do note that this implementation is geared towards development
    servers, and not for production usage.

    Producution usage should restrict the registry used to `nunja.mold`.
    """

    paths = {}

    for name in registries:
        registry = get(name)
        if not registry:
            logger.warning("registry '%s' does not exist", name)
            continue

        for key, value in registry.iter_records():
            # will simply overwrite with subsequent keys, much like how
            # the rest of the calmjs framework functions.
            paths[key] = name + '/' + key

    template = {
        "paths": paths,
        "baseUrl": base_url,
    }

    return template


def fetch(registry_name, mold_id_path):
    registry = get(registry_name)
    if not registry:
        raise KeyError("registry '%s' not found" % registry_name)

    try:
        path = registry.verify_path(mold_id_path)
    except OSError:
        raise KeyError("template at '%s' not found" % mold_id_path)

    with codecs.open(path, encoding='utf-8') as f:
        return f.read()


class BaseServer(object):
    """
    Base server implementation

    In practice, only one registry should be available as the default
    implementation only provide via a single registry to keep the
    overall system simple under production usage.
    """

    def __init__(self, base_url, registries=(ENTRY_POINT_NAME,)):
        self.base_url = base_url
        self.registries = registries
        self.requirejs_config = make_config(base_url, registries)

    def serve_config(self, path):
        return (UMD_REQUIREJS_JSON_EXPORT_HEADER +
            json_dumps(self.requirejs_config, indent=4) +
            UMD_REQUIREJS_JSON_EXPORT_FOOTER)

    def serve_template(self, path):
        """
        The path is the URL fragment after the base_url.
        """

        # grab the first fragment
        fragments = path.split('/', 1)
        if len(fragments) < 2:
            raise KeyError("invalid path")

        registry_name, mold_id_path = fragments

        if registry_name not in self.registries:
            raise KeyError("registry '%s' unavailable" % registry_name)

        return fetch(registry_name, mold_id_path)


class Server(BaseServer):
    """
    A more standard server implementation

    Only one registry will be active at a time.
    """

    def __init__(self, base_url, registry=ENTRY_POINT_NAME):
        registries = (registry,)
        super(Server, self).__init__(base_url, registries)
