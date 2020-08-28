from fastapi.testclient import TestClient
from .fixtures import in_context, patch_transaction
from google.cloud import ndb
from models import UserEmail

import main
import pytest

client = TestClient(main.app)

URL = "/email-address/"


@pytest.mark.usefixtures("in_context", "patch_transaction")
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


@pytest.mark.usefixtures("in_context", "patch_transaction")
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


@pytest.mark.usefixtures("in_context", "patch_transaction")
def test_email_address_delete(monkeypatch):
    data = {
        "api_key": "abcabc"
    }

    def delete(self):
        assert self == ndb.Key("UserEmail", data["api_key"])

    monkeypatch.setattr(ndb.Key, "delete", delete)

    r = client.delete(URL, json=data)

    assert r.status_code == 200
