from fastapi import FastAPI
from fastapi.testclient import TestClient
from google.cloud import ndb
from models import UserEmail


def test_email_address_new(monkeypatch):
    data = {
        "api_key": "abcabc",
        "email": "some@email.example"
    }

    def put(self):
        assert self == UserEmail(api_key=ndb.Key(
            "UserEmail", data["api_key"]), email=data["email"])

    monkeypatch.setattr(UserEmail, 'put', put)

    def get(self):
        return None

    monkeypatch.setattr(ndb.Key, 'get', get)

    def transaction(func):
        func()

    monkeypatch.setattr(ndb, 'transaction', transaction)

    from main import app

    client = TestClient(app)

    r = client.post(
        '/email-address/',
        json=data
    )
    print(r.text)
    assert r.status_code == 201


def test_email_address_update(monkeypatch):
    data = {
        "api_key": "abcabc",
        "email": "some@email.example"
    }

    def put(self):
        assert self == UserEmail(api_key=ndb.Key("UserEmail", data["api_key"]),
                                 email=data["email"])

    monkeypatch.setattr(UserEmail, 'put', put)

    def get(self):
        return UserEmail(api_key=ndb.Key("UserEmail", data["api_key"]),
                         email="random@email.example")

    monkeypatch.setattr(ndb.Key, 'get', get)

    def transaction(func):
        func()

    monkeypatch.setattr(ndb, 'transaction', transaction)

    from main import app

    client = TestClient(app)

    r = client.post(
        '/email-address/',
        json=data
    )
    print(r.text)
    assert r.status_code == 200
