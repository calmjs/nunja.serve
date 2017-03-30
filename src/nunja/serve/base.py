# -*- coding: utf-8 -*-
"""
Module for providing base classes.
"""

import codecs

from nunja.registry import ENTRY_POINT_NAME


def fetch(path):
    with codecs.open(path, encoding='utf-8') as f:
        return f.read()


class BaseProvider(object):
    """
    Base script provider implementation

    In practice, only one registry should be available as the default
    implementation only provide via a single registry to keep the
    overall system simple under production usage, however the base
    implementation support the cases for multiple registries.
    """

    def __init__(
            self, base_url, core_subpaths=(),
            registry_names=(ENTRY_POINT_NAME,)):
        """
        Arguments

        base_url
            The base url for which the provider will handle.  Typically
            this is a subpath on the root of the host (e.g `/scripts').
        core_subpaths
            The subpaths associated with this provider, which includes
            configuration files for the system attached, and also
            scripts that will initialise the front-end system.
        registry_names
            The nunja registries to load.
        """

        self.base_url = base_url
        self.core_subpaths = set(core_subpaths)
        self.registry_names = registry_names

    def fetch_core(self, identifier):
        """
        Serve a configuration file identified by the identifier
        """

        raise NotImplementedError

    def fetch_path(self, identifier):
        """
        Return the underlying filesystem path for the given object.
        """

        raise NotImplementedError

    def fetch_object(self, identifier):
        """
        Serve an object identified by the identifier; typically objects
        are the templates and/or the script files provided by the mold.

        The default implementation simply relies on the fetch_path
        method to acquire the filesystem path, and then call a function
        that simply return the contents at that location as a string.
        """

        path = self.fetch_path(identifier)
        return fetch(path)

    def fetch(self, path):
        """
        Generic fetch functionality.  Take a given path, attempt to
        return a value.

        Return value includes a string, or None if provided path is not
        matched by the base_url of this instance.  If matched subpath, a
        KeyError may be raised if the lookup failed.

        Typical implementation should be explicit and implement their
        own resolution techniques.
        """

        if not path.startswith(self.base_url):
            return None

        # normalize identifier by removing extra '/'s
        identifier = '/'.join(
            i for i in path[len(self.base_url):].split('/') if i)

        if identifier in self.core_subpaths:
            return self.fetch_core(identifier)
        return self.fetch_object(identifier)
