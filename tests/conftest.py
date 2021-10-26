import os
import shutil
from functools import partial
from pathlib import Path

import pytest

import bcdt.operator as op

TESTOP_PATH = os.path.join(os.path.dirname(__file__), "testop")


@pytest.fixture
def tmpoperator(tmpdir, monkeypatch):
    tmpOpsManager = op.manager.OperatorManager(tmpdir.dirname)
    monkeypatch.setattr(op.manager, "LocalOpsManager", tmpOpsManager)

    yield (Path(tmpdir), op)

    shutil.rmtree(tmpdir)


@pytest.fixture
def mock_download_repo(tmpoperator, monkeypatch, expected_repo_url=None):
    tmpdir, op = tmpoperator

    def _mock_download_repo(repo_url, operator_dir_name, expected_repo_url=None):
        """
        makes a mock function for the _download_repo function in bcdt.operator.manager.
        This mock function has an additional check to ensure the correct URL is
        generated for download.
        """
        if expected_repo_url is not None:
            assert repo_url == expected_repo_url
        op_dir = Path(tmpdir, operator_dir_name)
        shutil.copytree(TESTOP_PATH, op_dir)
        return op_dir.as_posix()

    monkeypatch.setattr(
        op.manager,
        "_download_repo",
        partial(_mock_download_repo, expected_repo_url=expected_repo_url),
    )

    yield op
