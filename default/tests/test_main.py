from fastapi import FastAPI
from fastapi.testclient import TestClient

from default.main import app

client = TestClient(app)

def test_index():
    response = client.get('/')
    assert response.status_code == 200
    with open('tests/testfiles/index.html', 'r') as correct:
        assert response.text == correct.read()
