from fastapi.testclient import TestClient
from main import app
from models import UserEmail

client = TestClient(app)


def test_index():
    r = client.get('/')
    assert r.status_code == 200
    assert r.json() == {"data": "Hello World"}
