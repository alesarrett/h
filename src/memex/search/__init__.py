# -*- coding: utf-8 -*-

from pyramid.settings import asbool

from memex.search.client import Client
from memex.search.config import configure_index
from memex.search.core import search
from memex.search.core import FILTERS_KEY
from memex.search.core import MATCHERS_KEY

__all__ = ('search',)


def _get_client(settings):
    """Return a client for the Elasticsearch index."""
    host = settings['es.host']
    index = settings['es.index']
    kwargs = {}
    kwargs['timeout'] = settings.get('es.client_timeout', 10)

    if 'es.client_poolsize' in settings:
        kwargs['maxsize'] = settings['es.client_poolsize']

    return Client(host, index, **kwargs)


def _legacy_get_client(settings):
    """Return a client for the legacy Elasticsearch index."""
    host = settings['es.host']
    index = settings['legacy.es.index']
    kwargs = {}
    kwargs['timeout'] = settings.get('es.client_timeout', 10)

    if 'es.client_poolsize' in settings:
        kwargs['maxsize'] = settings['es.client_poolsize']

    return Client(host, index, **kwargs)


def _get_client_or_legacy_client(request):
    """
    Return the Elasticsearch client.

    Returns a client for either the new Elasticsearch index (if the 'postgres'
    feature flag is on) or the legacy index (if the flag is off).

    """
    func = _get_client if request.feature('postgres') else _legacy_get_client
    return func(request.registry.settings)


def includeme(config):
    settings = config.registry.settings
    settings.setdefault('es.host', 'http://localhost:9200')
    settings.setdefault('es.index', 'hypothesis')
    settings.setdefault('legacy.es.index', 'annotator')

    # Allow users of this module to register additional search filter and
    # search matcher factories.
    config.registry[FILTERS_KEY] = []
    config.registry[MATCHERS_KEY] = []
    config.add_directive('add_search_filter',
                         lambda c, f: c.registry[FILTERS_KEY].append(f))
    config.add_directive('add_search_matcher',
                         lambda c, m: c.registry[MATCHERS_KEY].append(m))

    # Add a property to all requests for easy access to the elasticsearch
    # client. This can be used for direct or bulk access without having to
    # reread the settings.

    # request.legacy_es is always a client for the legacy Elasticsearch index,
    # regardless of whether the 'postgres' feature flag is on.
    # This should be used to write to the legacy search index.
    config.add_request_method(
        lambda r: _legacy_get_client(r.registry.settings),
        name='legacy_es',
        reify=True)

    # request.es is a client for either the new or the legacy Elasticsearch
    # index, depending on the 'postgres' feature flaf.
    # This should always be used to read from the search index.
    config.add_request_method(_get_client_or_legacy_client,
                              name='es',
                              reify=True)

    # If requested, automatically configure the index
    if asbool(settings.get('h.search.autoconfig', False)):
        configure_index(_get_client(settings))
        configure_index(_legacy_get_client(settings))
