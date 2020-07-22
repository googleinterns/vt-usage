from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import app
from models import UserEmail

client = TestClient(app)


def test_index():
    r = client.get('/')
    assert r.status_code == 200
    assert r.json() == {"data": "Hello World"}


correct_headers = {"X-Appengine-Inbound-Appid": "virustotal-step-2020"}


def test_query_results_empty_list():
    r = client.post(
        '/query-results/',
        headers=correct_headers,
        json={"data": [], "links": {}, "meta": {}})

    assert r.status_code == 200
    result = r.json()
    for name in ["data", "links", "meta"]:
        assert name in result
        assert len(result[name]) == 0


def test_query_results_normal_request():
    type_list = ["file", "url", "domain", "ip_address"]
    r = client.post(
        '/query-results/',
        headers=correct_headers,
        json={
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
    result = r.json()
    for obj in result["data"]:
        assert obj["attributes"] == {}
        assert obj["id"] == ""
        assert obj["links"] == {}
        assert obj["type"] in type_list


def test_query_results_bad_type():
    r = client.post(
        '/query-results/',
        headers=correct_headers,
        json={
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
        '/query-results/',
        headers=correct_headers,
        json={"data": [], "links": links, "meta": meta})

    assert r.status_code == 200
    result = r.json()
    assert result["data"] == []
    assert result["links"] == links
    assert result["meta"] == meta


def test_query_results_wrong_headers():
    r = client.post(
        '/query-results/',
        headers={},
        json={"data": [], "links": {}, "meta": {}})

    assert r.status_code == 403
    assert r.json() == {"detail": "Access forbidden"}


def test_query_missing_mandatory_field():
    request = {
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
        assert r.json()["detail"][0]["type"] == "value_error.missing"


def test_query_results_missing_field_in_data():
    obj = {
        "attributes": {},
        "id": "",
        "links": {},
        "type": "file"
    }

    for key in obj.keys():
        r = client.post(
            '/query-results/',
            headers=correct_headers,
            json={
                "data": [obj.copy().pop(key)],
                "links": {},
                "meta": {}
            })

        assert r.status_code == 422


def test_email_address_new(monkeypatch):
    data = {
        "api_key": "abcabc",
        "email": "some@email.example"
    }

    def put(udata):
        assert udata == UserEmail(api_key=data["api_key"], email=data["email"])
    
    monkeypatch.setattr(UserEmail, 'put', put)

    r = client.post(
        '/email-address/',
        json=data
    )

    assert r.status_code == 200
