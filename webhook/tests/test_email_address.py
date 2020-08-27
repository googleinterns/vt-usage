from fastapi import FastAPI
from fastapi.testclient import TestClient
from .fixtures import patch_ndb_client, patch_logger
from google.cloud import ndb
from models import UserEmail

import main
import pytest

client = TestClient(main.app)

URL = "/email-address/"


@pytest.fixture
def patch_transaction(monkeypatch):
    def transaction(func):
        func()

    monkeypatch.setattr(ndb, 'transaction', transaction)


@pytest.fixture(autouse=True)
def use_multiple_fixtures(patch_ndb_client, patch_logger, patch_transaction):
    # This wrapper will apply many fixtures to all tests.
    pass


def test_email_address_new(monkeypatch):
    data = {
        "api_key": "abcabc",
        "email": "some@email.example"
    }

    def put(self):
        assert self == UserEmail(id=data["api_key"], email=data["email"])

    monkeypatch.setattr(UserEmail, "put", put)

    def get(self):
        return None

    monkeypatch.setattr(ndb.Key, "get", get)

    r = client.post(URL, json=data)

    assert r.status_code == 201


def test_email_address_update(monkeypatch):
    data = {
        "api_key": "abcabc",
        "email": "some@email.example"
    }

    def put(self):
        assert self == UserEmail(id=data["api_key"],
                                 email=data["email"])

    monkeypatch.setattr(UserEmail, "put", put)

    def get(self):
        return UserEmail(id=data["api_key"],
                         email="random@email.example")

    monkeypatch.setattr(ndb.Key, "get", get)

    r = client.post(URL, json=data)

    assert r.status_code == 200


def test_email_address_delete(monkeypatch):
    data = {
        "api_key": "abcabc"
    }

    def delete(self):
        assert self == ndb.Key("UserEmail", data["api_key"])

    monkeypatch.setattr(ndb.Key, "delete", delete)

    r = client.delete(URL, json=data)

    assert r.status_code == 200
