from fastapi import FastAPI
from fastapi.testclient import TestClient

from webhook.main import app

client = TestClient(app)


def test_index():
    r = client.get('/')
    assert r.status_code == 200
    assert r.json() == {"data": "Hello World"}


correct_headers = {"X-Appengine-Inbound-Appid": "virustotal-step-2020"}


def test_query_results_str():
    r = client.post(
        '/query-results/',
        headers=correct_headers,
        json={"data": "str"})
    assert r.status_code == 200
    assert "data" in r.json()
    assert r.json()["data"] == "str"


def test_query_results_list():
    r = client.post(
        '/query-results/',
        headers=correct_headers,
        json={"data": []})
    assert r.status_code == 200
    assert "data" in r.json()
    assert r.json()["data"] == []


def test_query_results_dict():
    r = client.post(
        '/query-results/',
        headers=correct_headers,
        json={"data": {}})
    assert r.status_code == 200
    assert r.json()["data"] == {}


def test_query_results_wrong_headers():
    r = client.post(
        '/query-results/',
        headers={"Some": "nonsense"},
        json={"data": {}})

    assert r.status_code == 403
    assert r.json() == {"detail": "Access forbidden"}


def test_query_results_no_data():
    r = client.post(
        '/query-results/',
        headers=correct_headers,
        json={"links": {"self": "https://www.virustotal.com"}})

    assert r.status_code == 422
    assert r.json()["detail"][0]["type"] == "value_error.missing"


def test_query_results_additional_fields():
    r = client.post(
        '/query-results/',
        headers=correct_headers,
        json={
            "data": [{}, {"another": "dict"}, {}],
            "links": {"self": "https://www.virustotal.com"},
            'meta': {'count': 0}
        })

    assert r.status_code == 200
    assert r.json()["data"] == [{}, {"another": "dict"}, {}]
    assert r.json()["links"] == {"self": "https://www.virustotal.com"}
    assert r.json()["meta"] == {'count': 0}
