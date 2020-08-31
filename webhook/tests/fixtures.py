from contextlib import contextmanager
from unittest import mock

from google.cloud import ndb
from google.cloud.ndb import context as context_module

import pytest


@pytest.fixture
def in_context(monkeypatch):
    """
    This fixture will create a context that won't connect to the datastore.
    At the same time it will mock context used in the code to do nothing
    to prevent double context creation.
    """
    ndb_client = mock.Mock(
        project="testing",
        namespace=None,
        stub=mock.Mock(spec=()),
        spec=("project", "namespace", "stub"),
    )
    context = context_module.Context(ndb_client).use()
    context.__enter__()

    class MockContext:
        @contextmanager
        def context(self):
            yield None

    def client():
        return MockContext()

    monkeypatch.setattr(ndb, 'Client', client)

    yield

    context.__exit__(None, None, None)


@pytest.fixture
def patch_transaction(monkeypatch):
    def transaction(func):
        func()

    monkeypatch.setattr(ndb, 'transaction', transaction)
