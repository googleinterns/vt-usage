from fastapi.testclient import TestClient
from fastapi import UploadFile

from os import path

import builtins
import main
import tempfile
import pytest

client = TestClient(main.app)


def test_homepage():
    response = client.get('/')
    assert response.status_code == 200
    assert response.template.name == "form.html.jinja"
    assert "request" in response.context


def test_download_file_ok(monkeypatch):
    f = tempfile.NamedTemporaryFile()
    content = b"This is an example \x00\xff"
    f.write(content)
    f.seek(0)

    def join(a, b):
        return f.name

    monkeypatch.setattr(path, "join", join)

    response = client.get('/1111')

    assert response.content == content
    f.close()


@pytest.mark.parametrize("file_name", [
    "some-file", "../main.py"
])
def test_download_file_bad(file_name):
    response = client.get(file_name)
    assert response.status_code == 400


def test_upload_file(monkeypatch):
    def open(path, type):
        return tempfile.TemporaryFile()

    monkeypatch.setattr(builtins, "open", open)

    response = client.post("/upload-file/",
                           headers={"Content-Type": "multipart/form-data"},
                           data={
                               "file": b"bytesbytes"
                           })

    assert response.status_code == 200
    assert response.template.name == "file_name.html.jinja"
    assert "request" in response.content
    assert "name" in response.content
