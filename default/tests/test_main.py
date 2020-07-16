from fastapi import FastAPI
from fastapi.testclient import TestClient

from default.main import app, models

client = TestClient(app)

def test_index():
    response = client.get('/')
    assert response.status_code == 200
    with open('tests/testfiles/index.html', 'r') as correct:
        assert response.text == correct.read()


def test_userdata(monkeypatch):
    def put(udata):
        assert udata == models.Userdata(apikey='test_apikey', webhook='test_webhook')

    monkeypatch.setattr(models.Userdata, 'put', put)
    response = client.post(
        '/userdata/',
        data={
            'apikey': 'test_apikey',
            'webhook': 'test_webhook',
        })
    assert response.status_code == 200
    with open('tests/testfiles/userdata.html', 'r') as correct:
        assert response.text == correct.read()


def test_wrong_userdata():
    response = client.post(
        '/userdata/',
        data={
            'apikey': 'test_apikey',
        })
    assert response.status_code == 422

    response = client.post(
        '/userdata/',
        data={
            'webhook': 'test_webhook',
        })
    assert response.status_code == 422
