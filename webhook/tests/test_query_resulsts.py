from fastapi import FastAPI
from fastapi.testclient import TestClient
from main import app


correct_headers = {"X-Appengine-Inbound-Appid": "virustotal-step-2020"}
client = TestClient(app)

URL = "/query-results/"


def test_query_results_empty_list():
    r = client.post(
        URL,
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
        URL,
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
        URL,
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
        URL,
        headers=correct_headers,
        json={"data": [], "links": links, "meta": meta})

    assert r.status_code == 200
    result = r.json()
    assert result["data"] == []
    assert result["links"] == links
    assert result["meta"] == meta


def test_query_results_wrong_headers():
    r = client.post(
        URL,
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
            URL,
            headers=correct_headers,
            json={
                "data": [obj.copy().pop(key)],
                "links": {},
                "meta": {}
            })

        assert r.status_code == 422
