from unittest import mock

from fastapi.testclient import TestClient
from google.cloud.ndb import context as context_module
from .fixtures import patch_ndb_client
from google.cloud import ndb

from unittest import mock
from google.cloud import ndb
from google.cloud.ndb import context as context_module

import main
import models
import pytest

client = TestClient(main.app)

URL = "/email-address/"


@pytest.fixture
def patch_transaction(monkeypatch):
    def transaction(func):
        func()

    monkeypatch.setattr(ndb, 'transaction', transaction)


@pytest.fixture(autouse=True)
def use_multiple_fixtures(patch_ndb_client, patch_transaction):
    # This wrapper will apply many fixtures to all tests.
    pass


# @pytest.mark.usefixtures("in_context")
# def test_email_address_new(patch_transaction, monkeypatch):
#     data = {
#         "api_key": "abcabc",
#         "email": "some@email.example"
#     }
#
#     class Key:
#         name: str
#         id: str
#
#         def __init__(self, name, id):
#             self.name = name
#             self.id = id
#
#         def get(self):
#             return None
#
#     monkeypatch.setattr(ndb, "Key", Key)
#
#     # def get_context(raise_context_error=False):
#     #     pass
#     #
#     # monkeypatch.setattr(context_module, "get_context", get_context)
#
#     # class UserEmail:
#     #     id: str
#     #     email: str
#     #
#     #     def __init__(self, id, email):
#     #         self.id = id
#     #         self.email = email
#     #
#     #     def put(self):
#     #         pass
#     #
#     # models.UserEmail = UserEmail
#
#     ndb_client = mock.Mock(
#         project="testing",
#         namespace=None,
#         stub=mock.Mock(spec=()),
#         spec=("project", "namespace", "stub"),
#     )
#     context = context_module.Context(ndb_client).use()
#     context.__enter__()
#
#     r = client.post(URL, json=data)
#     assert r.status_code == 201





def test_email_address_update(monkeypatch):
    data = {
        "api_key": "abcabc",
        "email": "some@email.example"
    }

    ndb_client = mock.Mock(
        project="testing",
        namespace=None,
        stub=mock.Mock(spec=()),
        spec=("project", "namespace", "stub"),
    )
    context = context_module.Context(ndb_client).use()
    context.__enter__()

    def put(self):
        assert self == models.UserEmail(id=data["api_key"],
                                 email=data["email"])

    monkeypatch.setattr(models.UserEmail, "put", put)

    def get(self):
        return models.UserEmail(id=data["api_key"],
                         email="random@email.example")

    monkeypatch.setattr(ndb.Key, "get", get)

    r = client.post(URL, json=data)

    assert r.status_code == 200
#
#
# def test_email_address_delete(monkeypatch):
#     data = {
#         "api_key": "abcabc"
#     }
#
#     def delete(self):
#         assert self == ndb.Key("UserEmail", data["api_key"])
#
#     monkeypatch.setattr(ndb.Key, "delete", delete)
#
#     r = client.delete(URL, json=data)
#
#     assert r.status_code == 200
