# -*- coding: utf-8 -*-

import functools
import os

import mock
import pytest
from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker

from memex import db

Session = scoped_session(sessionmaker())


def autopatcher(request, target, **kwargs):
    """Patch and cleanup automatically. Wraps :py:func:`mock.patch`."""
    options = {'autospec': True}
    options.update(kwargs)
    patcher = mock.patch(target, **options)
    obj = patcher.start()
    request.addfinalizer(patcher.stop)
    return obj


@pytest.fixture
def config(request, settings):
    """Pyramid configurator object."""
    from pyramid import testing
    config = testing.setUp(settings=settings)
    request.addfinalizer(testing.tearDown)
    return config


@pytest.fixture(scope='session')
def settings():
    """Default app settings."""
    settings = {}
    settings['sqlalchemy.url'] = os.environ.get('TEST_DATABASE_URL',
                                                'postgresql://postgres@localhost/htest')
    return settings


@pytest.fixture(autouse=True)
def db_session(request, monkeypatch):
    """
    Prepare the SQLAlchemy session object.

    We enable fast repeatable database tests by setting up the database only
    once per session (see :func:`setup_database`) and then wrapping each test
    function in a SAVEPOINT/ROLLBACK TO SAVEPOINT within the transaction.
    """
    Session.begin_nested()
    request.addfinalizer(Session.rollback)

    # Prevent the session from committing, but simulate the effects of a commit
    # within our transaction. N.B. we must not only flush SQLA state to the
    # database but also expire the persistence state of all objects.
    def _fake_commit():
        Session.flush()
        Session.expire_all()
    monkeypatch.setattr(Session, 'commit', _fake_commit)
    # Prevent the session from closing (make it a no-op):
    monkeypatch.setattr(Session, 'remove', lambda: None)
    return Session


@pytest.fixture(scope='module', autouse=True)
def setup_database(request, settings):
    """Set up the database connection and create tables."""
    engine = engine_from_config(settings, 'sqlalchemy.')
    db.bind_engine(engine, should_create=True, should_drop=True)
    db.use_session(Session)
    request.addfinalizer(Session.remove)


@pytest.fixture
def patch(request):
    return functools.partial(autopatcher, request)
