from fastapi import FastAPI
from fastapi.testclient import TestClient
from main import app
from models import UserEmail
from google.cloud import ndb

import pytest

correct_headers = {"X-Appengine-Inbound-Appid": "virustotal-step-2020"}
client = TestClient(app)

URL = "/query-results/"
API_KEY = "abc123"


@pytest.fixture
def patch_key_get_default_email(monkeypatch):
    def get(self):
        return UserEmail(id="123abc", email="sample@email.address")

    monkeypatch.setattr(ndb.Key, 'get', get)


def test_query_results_empty_list(patch_key_get_default_email):
    r = client.post(
        URL,
        headers=correct_headers,
        json={"api_key": API_KEY, "data": [], "links": {}, "meta": {}})

    assert r.status_code == 200


def test_query_results_normal_request(patch_key_get_default_email):
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
            "meta": {}
        })

    assert r.status_code == 200


def test_query_results_bad_type(patch_key_get_default_email):
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


def test_query_results_links_and_meta(patch_key_get_default_email):
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
        json={"api_key": API_KEY, "data": [], "links": links, "meta": meta})

    assert r.status_code == 200


def test_query_results_wrong_headers(patch_key_get_default_email):
    r = client.post(
        URL,
        headers={},
        json={"api_key": API_KEY, "data": [], "links": {}, "meta": {}})

    assert r.status_code == 403
    assert r.json() == {"detail": "Access forbidden"}


def test_query_missing_mandatory_field(patch_key_get_default_email):
    request = {
        "api_key": API_KEY,
        "data": [],
        "links": {},
        "meta": {}
    }

    for key in request.keys():
        r = client.post(
            '/query-results/',
            headers=correct_headers,
            json=request.copy().pop(key))

        assert r.status_code == 422


def test_query_results_missing_field_in_data(patch_key_get_default_email):
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
                "meta": {}
            })

        assert r.status_code == 422
