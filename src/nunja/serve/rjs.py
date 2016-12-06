# -*- coding: utf-8 -*-
"""
For requirejs
"""

import logging
from calmjs.registry import get

logger = logging.getLogger(__name__)


def make_config(base_url, registries=('nunja.mold',)):
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
