import os

import pytest

from bentoctl.operator import utils as operator_utils


def test_get_bentoctl_home(tmp_path):
    os.environ["BENTOCTL_HOME"] = str(tmp_path)
    bentoctl_home = operator_utils._get_bentoctl_home()
    assert bentoctl_home == tmp_path
    assert (tmp_path / "operators").exists()


@pytest.mark.parametrize(
    "git_link, truth",
    [
        ("git@gitlab.com:nick.thomas/gitaly.git", True),
        ("https://gitlab.com/nick.thomas/gitaly.git", True),
        ("git@github.com:bentoml/aws-sagemaker-deploy.git", True),
        ("https://github.com/bentoml/aws-sagemaker-deploy.git", True),
    ],
)
def test_is_git_link(git_link, truth):
    assert operator_utils._is_git_link(git_link) is truth


@pytest.mark.parametrize(
    "github_repo, truth",
    [
        ("bentoml/sagemaker", True),
        ("bentoml/aws-lambda:test", True),
        ("notgitrepo", False),
    ],
)
def test_is_github_repo(github_repo, truth):
    assert operator_utils._is_github_repo(github_repo) is truth


@pytest.mark.parametrize(
    "official_op, truth", [("aws-lambda", True), ("testop", False)]
)
def test_is_official_operator(official_op, truth):
    assert operator_utils._is_official_operator(official_op) is truth


def test_get_operator_dir_path(tmp_path):
    os.environ["BENTOCTL_HOME"] = str(tmp_path)
    op_dir = operator_utils._get_operator_dir_path(operator_name="test_operator")
    assert op_dir == str(tmp_path / "operators" / "test_operator")
