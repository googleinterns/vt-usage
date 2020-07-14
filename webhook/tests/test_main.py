from fastapi import FastAPI
from fastapi.testclient import TestClient

from webhook.main import app

client = TestClient(app)

def test_index():
    response = client.get('/')
    assert response.status_code == 200
    assert response.text == '{"data":"Hello World"}'
