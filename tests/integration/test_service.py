from io import StringIO
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
    FILE_CONTENT = "mock file"
    file = StringIO(FILE_CONTENT)
    resp = r.post(
        urljoin(url, "test_file"),
        data=file,
        headers={"Content-Type": "application/octet-stream"},
    )
    assert resp.ok
    assert resp.content == FILE_CONTENT.encode()


def test_multipart(url):
    file = StringIO("mock file")
    resp = r.post(
        urljoin(url, "test_multipart"),
        files={"arr": "[1, 2, 3, 4]", "file": (None, file, "application/octet-stream")},
    )
    assert resp.ok


def test_sklearn_runner(url):
    resp = r.post(urljoin(url, "sklearn_runner"), json=[[1, 2, 3, 4]])
    assert resp.ok
    assert resp.json() == [2]
