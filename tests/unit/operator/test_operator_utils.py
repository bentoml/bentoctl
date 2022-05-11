import os
from pathlib import Path
from types import SimpleNamespace

import pytest

import bentoctl.operator.utils as operator_utils

# import bentoctl.operator.utils.git
# from bentoctl.operator import utils as operator_utils


def test_get_bentoctl_home(tmp_path):
    os.environ["BENTOCTL_HOME"] = str(tmp_path)
    bentoctl_home = operator_utils._get_bentoctl_home()
    assert bentoctl_home == tmp_path
    assert (tmp_path / "operators").exists()


@pytest.mark.parametrize(
    "official_op, truth", [("aws-lambda", True), ("testop", False)]
)
def test_is_official_operator(official_op, truth):
    assert operator_utils._is_official_operator(official_op) is truth


def test_get_operator_dir_path(tmp_path):
    os.environ["BENTOCTL_HOME"] = str(tmp_path)
    op_dir = operator_utils._get_operator_dir_path(operator_name="test_operator")
    assert op_dir == str(tmp_path / "operators" / "test_operator")


class PatchedRepo:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.git = SimpleNamespace()
        self.git.checkout = self.checkout

    @classmethod
    def clone_from(cls, _, repo_path):
        return cls(repo_path)

    def checkout(self, branch):
        Path(self.repo_path / branch).touch()
