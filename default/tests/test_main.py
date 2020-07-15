from fastapi import FastAPI
from fastapi.testclient import TestClient

from default.main import app, datastore_client

client = TestClient(app)

def test_index():
    response = client.get('/')
    assert response.status_code == 200
    with open('tests/testfiles/index.html', 'r') as correct:
        assert response.text == correct.read()


def test_userdata():
    response = client.post(
        '/userdata/',
        data={
            'apikey': 'test_apikey',
            'webhook': 'test_webhook',
        })
    assert response.status_code == 200
    with open('tests/testfiles/userdata.html', 'r') as correct:
        assert response.text == correct.read()
    
    query = datastore_client.query(kind='userdata')
    query.add_filter('apikey', '=', 'test_apikey')
    result = list(query.fetch())
    assert result != []
    key = result[0].key
    datastore_client.delete(key)
