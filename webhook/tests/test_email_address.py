# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
