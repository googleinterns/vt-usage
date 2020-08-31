from datetime import datetime
from fastapi.testclient import TestClient
from .fixtures import in_context
from models import UserEmail
from google.cloud import ndb

import jwt
import main
import pytest

correct_headers = {"X-Appengine-Inbound-Appid": "virustotal-step-2020"}
client = TestClient(main.app)

URL = "/query-results/"
API_KEY = "abc123"


@pytest.fixture
def key_get_email(monkeypatch):
    def get(self):
        return UserEmail(id="123abc", email="sample@email.address")

    monkeypatch.setattr(ndb.Key, 'get', get)


@pytest.fixture
def patch_get_secret(monkeypatch):
    def get(*args, **kwargs):
        return 'SECRET'

    monkeypatch.setattr(main, 'get_secret', get)

    def decode(*args, **kwargs):
        return {'issued': datetime.now().isoformat()}

    monkeypatch.setattr(jwt, 'decode', decode)


@pytest.mark.usefixtures("in_context", "key_get_email", "patch_get_secret")
def test_query_results_empty_list():
    r = client.post(
        URL,
        headers=correct_headers,
        json={"api_key": API_KEY, "data": [], "links": {}, "meta": {}, "jwt_token": "token"})

    assert r.status_code == 200


@pytest.mark.usefixtures("in_context", "key_get_email", "patch_get_secret")
def test_query_results_normal_request():
    type_list = ["file", "url", "domain", "ip_address"]
    r = client.post(
        URL,
        headers=correct_headers,
        json={
            "api_key": API_KEY,
            "data": [{
                "attributes": {},
                "id": "",
                "links": {},
                "type": t
            } for t in type_list],
            "links": {},
            "meta": {},
            "jwt_token": "token"
        })

    assert r.status_code == 200


@pytest.mark.usefixtures("in_context", "key_get_email")
def test_query_results_bad_type():
    r = client.post(
        URL,
        headers=correct_headers,
        json={
            "api_key": API_KEY,
            "data": [{
                "attributes": {},
                "id": "",
                "links": {},
                "type": "other_type"
            }],
            "links": {},
            "meta": {}
        })

    assert r.status_code == 422


@pytest.mark.usefixtures("in_context", "key_get_email", "patch_get_secret")
def test_query_results_links_and_meta():
    links = {
        "self": "https://google.com",
        "next": "https://gmail.com",
        "strange": "not-url-for-sure"
    }
    meta = {
        "count": 0,
        "something": "other"
    }

    r = client.post(
        URL,
        headers=correct_headers,
        json={"api_key": API_KEY, "data": [], "links": links, "meta": meta, 'jwt_token': 'token'})

    assert r.status_code == 200


@pytest.mark.skip('Don\'t need to check authentication for now')
@pytest.mark.usefixtures("in_context", "key_get_email")
def test_query_results_wrong_headers():
    r = client.post(
        URL,
        headers={},
        json={"api_key": API_KEY, "data": [], "links": {}, "meta": {}, 'jwt_token': 'token'})

    assert r.status_code == 403
    assert r.json() == {"detail": "Access forbidden"}


@pytest.mark.usefixtures("in_context", "key_get_email")
def test_query_missing_mandatory_field():
    request = {
        "api_key": API_KEY,
        "data": [],
        "links": {},
        "meta": {},
        "jwt_token": "token"
    }

    for key in request.keys():
        r = client.post(
            '/query-results/',
            headers=correct_headers,
            json=request.copy().pop(key))

        assert r.status_code == 422


@pytest.mark.usefixtures("in_context", "key_get_email")
def test_query_results_missing_field_in_data():
    obj = {
        "attributes": {},
        "id": "",
        "links": {},
        "type": "file"
    }

    for key in obj.keys():
        r = client.post(
            URL,
            headers=correct_headers,
            json={
                "api_key": API_KEY,
                "data": [obj.copy().pop(key)],
                "links": {},
                "meta": {},
                "jwt_token": "token"
            })

        assert r.status_code == 422
