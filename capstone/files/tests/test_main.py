from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_index():
    response = client.get('/')
    assert response.status_code == 200
    assert response.status_code == 200
    assert response.template.name == "form.html.jinja"
    assert "request" in response.context


