import os
from urllib.parse import urljoin

import requests as r


def test_alive(url, target):
    if target == "sagemaker":
        endpoint = urljoin(url, "ping")
    else:
        endpoint = urljoin(url, "livez")

    resp = r.get(endpoint)
    assert resp.ok


def test_json(url):
    resp = r.post(urljoin(url, "test_json"), json={"test": "something"})
    assert resp.ok
    assert resp.json() == {"test": "something"}


def test_file(url):
    file_path = os.path.join(os.path.dirname(__file__), "./README.md")
    file = open(file_path, "rb")
    resp = r.post(
        urljoin(url, "test_file"),
        data=file,
        headers={"Content-Type": "application/octet-stream"},
    )
    assert resp.ok
    file.seek(0)  # seek to begining
    assert resp.content == file.read()
    file.close()


def test_multipart(url):
    file_path = os.path.join(os.path.dirname(__file__), "./README.md")
    file = open(file_path, "rb")
    resp = r.post(
        urljoin(url, "test_multipart"),
        files={"arr": "[1, 2, 3, 4]", "file": (None, file, "application/octet-stream")},
    )
    assert resp.ok
