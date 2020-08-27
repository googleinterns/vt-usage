from contextlib import contextmanager
from google.cloud import ndb

import main
import pytest


class MockContext:
    @contextmanager
    def context(self):
        try:
            yield None
        except:
            pass


@pytest.fixture
def patch_ndb_client(monkeypatch):
    def client():
        return MockContext()
    monkeypatch.setattr(ndb, 'Client', client)


@pytest.fixture
def patch_logger(monkeypatch):
    def setup_cloud_logging():
        pass

    monkeypatch.setattr(main, 'setup_cloud_logging', setup_cloud_logging)