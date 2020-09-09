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

import aiohttp
import pytest
from contextlib import contextmanager
from fastapi import FastAPI
from fastapi.testclient import TestClient
from google.cloud import ndb
from unittest.mock import ANY, patch, call
from asynctest import CoroutineMock, MagicMock as AsyncMagicMock, patch as asyncpatch

import main

client = TestClient(main.app)

def test_index():
    response = client.get('/')
    assert response.status_code == 200
    with open('tests/testfiles/index.html', 'r') as correct:
        assert response.text == correct.read()


class MockContext:
    @contextmanager
    def context(self):
        yield None


@pytest.fixture
def patch_ndb_client(monkeypatch):
    def client():
        return MockContext()
    monkeypatch.setattr(ndb, 'Client', client)


@pytest.mark.parametrize('webhook', [
        'webhook.com',
        'test.webhook.com',
        'https://web_hook.com',
        'webhook.com/a+b+c',
        'http://webhook.com/#1a',
        'webhook.com:80/'
        'http://test.webhook.com:8080/a/b/c_?d=e',
    ])
def test_userdata(webhook, monkeypatch, patch_ndb_client):
    def put(udata):
        assert udata == main.models.Userdata(apikey='test_apikey', webhook=webhook, vt_query='test_vt_query')

    monkeypatch.setattr(main.models.Userdata, 'put', put)
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


def test_wrong_userdata(patch_ndb_client):
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


@patch('main.get_secret', return_value='SECRET')
@patch('main.models.Userdata.query', return_value=[main.models.Userdata(apikey='test_apikey', webhook='test_webhook', vt_query='test_vt_query')])
@asyncpatch('aiohttp.ClientSession.get')
@asyncpatch('aiohttp.ClientSession.post')
def test_run_queries(mock_post, mock_get, mock_q, mock_secret, patch_ndb_client):
    test_vt_data = {'api_key': 'test_apikey', 'data': ['test_data'], 'links': {'self': 'test_self'}, 'meta': {'test_meta': 'test_meta'}, 'jwt_token': 'resp_text'}

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
    main.models.Userdata.query.assert_called_once()
    aiohttp.ClientSession.get.assert_called_once_with('https://www.virustotal.com/api/v3/intelligence/search?query=test_vt_query', headers=ANY, ssl=ANY)
    aiohttp.ClientSession.post.assert_has_calls(
        [call('https://webhook-dot-virustotal-step-2020.ew.r.appspot.com/', json={'access_key': 'SECRET', 'vt_key': 'test_apikey'}, ssl=ANY),
         call('test_webhook', json=test_vt_data, ssl=ANY)], any_order=True)



def test_bad_run_queries(patch_ndb_client):
    response = client.get(
        '/run_queries/'
    )
    assert response.status_code == 403
