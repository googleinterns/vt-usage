import aiohttp
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import ANY, patch
from asynctest import CoroutineMock, MagicMock as AsyncMagicMock, patch as asyncpatch

from main import app, models

client = TestClient(app)

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


@patch('models.Userdata.query', return_value=[models.Userdata(apikey='test_apikey', webhook='test_webhook', vt_query='test_vt_query')])
@asyncpatch('aiohttp.ClientSession.get')
@asyncpatch('aiohttp.ClientSession.post')
def test_run_queries(mock_post, mock_get, mock_q):
    test_vt_data = {'api_key': 'test_apikey', 'data': ['test_data'], 'links': {'self': 'test_self'}, 'meta': {'test_meta': 'test_meta'}}

    mock_get.return_value.__aenter__.return_value.json = CoroutineMock()
    mock_get.return_value.__aenter__.return_value.status = 200
    mock_get.return_value.__aenter__.return_value.json.return_value = test_vt_data
    mock_post.return_value.__aenter__.return_value.text = CoroutineMock()
    mock_post.return_value.__aenter__.return_value.status = 200
    mock_post.return_value.__aenter__.return_value.text.return_value = "resp_text"

    response = client.get(
        '/run_queries/',
        headers={'X-Appengine-Cron': 'true'}
    )

    assert response.status_code == 200
    assert response.text == '"Success"'
    models.Userdata.query.assert_called_once()
    aiohttp.ClientSession.get.assert_called_once_with('https://www.virustotal.com/api/v3/intelligence/search?query=test_vt_query', headers=ANY, ssl=ANY)
    aiohttp.ClientSession.post.assert_called_once_with('test_webhook', json=test_vt_data, headers={'Signature': ANY},ssl=ANY)



def test_bad_run_queries():
    response = client.get(
        '/run_queries/'
    )
    assert response.status_code == 403
