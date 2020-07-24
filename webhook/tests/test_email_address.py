from fastapi import FastAPI
from fastapi.testclient import TestClient
from google.cloud import ndb
from main import app
from models import UserEmail

import pytest

client = TestClient(app)

URL = "/email-address/"


@pytest.fixture(autouse=True)
def patch_transaction(monkeypatch):
    def transaction(func):
        func()

    monkeypatch.setattr(ndb, 'transaction', transaction)


def test_email_address_new(monkeypatch):
    data = {
        "api_key": "abcabc",
        "email": "some@email.example"
    }

    def put(self):
        assert self == UserEmail(api_key=ndb.Key(
            "UserEmail", data["api_key"]), email=data["email"])

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
        assert self == UserEmail(api_key=ndb.Key("UserEmail", data["api_key"]),
                                 email=data["email"])

    monkeypatch.setattr(UserEmail, "put", put)

    def get(self):
        return UserEmail(api_key=ndb.Key("UserEmail", data["api_key"]),
                         email="random@email.example")

    monkeypatch.setattr(ndb.Key, "get", get)

    r = client.post(URL, json=data)

    assert r.status_code == 200
