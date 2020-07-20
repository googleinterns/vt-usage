import requests
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from main import app, models

client = TestClient(app)

class MockHTTPResponse:
    def __init__(self, data=None):
        self.data = data
    
    def json(self):
        return self.data

def test_index():
    response = client.get('/')
    assert response.status_code == 200
    with open('tests/testfiles/index.html', 'r') as correct:
        assert response.text == correct.read()


def test_userdata(monkeypatch):
    webhooks = [
        'webhook.com',
        'test.webhook.com',
        'https://web_hook.com',
        'webhook.com/a+b+c',
        'http://webhook.com/#1a',
        'webhook.com:80/'
        'http://test.webhook.com:8080/a/b/c_?d=e',
    ]

    for webhook in webhooks:
        def put(udata):
            assert udata == models.Userdata(apikey='test_apikey', webhook=webhook, vt_query='test_vt_query')

        monkeypatch.setattr(models.Userdata, 'put', put)
        response = client.post(
            '/userdata/',
            data={
                'apikey': 'test_apikey',
                'webhook': webhook,
                'vt_query': 'test_vt_query'
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
            'webhook': 'test_webhook.com',
        })
    assert response.status_code == 422

    response = client.post(
        '/userdata/',
        data={
            'apikey': 'test_apikey',
            'webhook': 'test_webhook',
        })
    assert response.status_code == 422

    response = client.post(
        '/userdata/',
        data={
            'apikey': 'test_apikey',
            'webhook': 'test_webhook',
            'vt_query': 'test_vt_query',
        })
    assert response.status_code == 400


def test_run_queries():
    test_vt_data = {'data': ['test_data'], 'links': {'self': 'test_self'}, 'meta': {'test_meta': 'test_meta'}}
    models.Userdata.query = MagicMock(return_value=[models.Userdata(apikey='test_apikey', webhook='test_webhook', vt_query='test_vt_query')])
    requests.get = MagicMock(return_value=MockHTTPResponse(test_vt_data))
    requests.post = MagicMock()

    response = client.get(
        '/run_queries/',
        headers={'X-Appengine-Cron': 'true'}
    )

    assert response.status_code == 200
    assert response.text == '"Success"'
    models.Userdata.query.assert_called_once()
    requests.get.assert_called_once_with('https://www.virustotal.com/api/v3/intelligence/search?query=test_vt_query', headers={'x-apikey': 'test_apikey'})
    requests.post.assert_called_once_with('test_webhook', test_vt_data)


def test_bad_run_queries():
    response = client.get(
        '/run_queries/'
    )
    assert response.status_code == 403
