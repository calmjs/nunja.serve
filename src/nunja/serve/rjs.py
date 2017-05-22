# -*- coding: utf-8 -*-
"""
Demo serving implementation based on the requirejs backed module system
and plugin for serving/retrieving template.

The goal is to provide a live-reloading server implementation for usage
during the development phase of a given library.
"""

import logging

from calmjs.utils import json_dumps
from calmjs.registry import get
from calmjs.rjs.umdjs import UMD_REQUIREJS_JSON_EXPORT_HEADER
from calmjs.rjs.umdjs import UMD_REQUIREJS_JSON_EXPORT_FOOTER
from nunja.registry import ENTRY_POINT_NAME

from nunja.serve import base

logger = logging.getLogger(__name__)

# XXX the provided names, along with the init template, should be
# deferred to some upstream helper specific to the current module
# framework that is being used.
default_init_script = """'use strict';
require(['nunja/index'], function() {});
"""


def make_config(base_url, registry_names=(ENTRY_POINT_NAME,)):
    """
    Return a configuration for requirejs to function against some end
    point.

    Do note that this implementation is geared towards development
    servers, and not for production usage.

    Producution usage should restrict the registry used to `nunja.mold`.
    """

    paths = {}

    for name in registry_names:
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


def get_path(registry_name, mold_id_path):
    registry = get(registry_name)
    if not registry:
        raise KeyError("registry '%s' not found" % registry_name)

    try:
        path = registry.verify_path(mold_id_path)
    except OSError:
        raise KeyError("template at '%s' not found" % mold_id_path)

    return path


class Provider(base.BaseProvider):
    """
    A more standard server implementation

    Only one registry will be active at a time.
    """

    def __init__(
            self, base_url,
            core_subpaths=('config.js', 'init.js',),
            init_script=default_init_script,
            registry_names=(ENTRY_POINT_NAME,),
            ):
        super(Provider, self).__init__(
            base_url, core_subpaths, registry_names)

        self.init_script = init_script
        self.requirejs_config = make_config(self.base_url, self.registry_names)

        self.core_subpaths = dict(zip(
            core_subpaths, [self.build_config(), init_script]))

    def fetch_core(self, identifier):
        return self.core_subpaths[identifier]

    def build_config(self):
        return (
            UMD_REQUIREJS_JSON_EXPORT_HEADER +
            json_dumps(self.requirejs_config, indent=4) +
            UMD_REQUIREJS_JSON_EXPORT_FOOTER
        )

    def fetch_path(self, identifier):
        """
        Return the path of the source identified by the identifier.
        """

        # grab the first fragment
        fragments = identifier.split('/', 1)
        if len(fragments) < 2:
            raise KeyError("invalid identifier")

        registry_name, mold_id_path = fragments

        if registry_name not in self.registry_names:
            raise KeyError("registry '%s' unavailable" % registry_name)

        return get_path(registry_name, mold_id_path)
