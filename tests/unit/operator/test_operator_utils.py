import os
from pathlib import Path
from types import SimpleNamespace

import pytest

import bentoctl.operator.utils
import bentoctl.operator.utils.git
from bentoctl.operator import utils as operator_utils


def test_get_bentoctl_home(tmp_path):
    os.environ["BENTOCTL_HOME"] = str(tmp_path)
    bentoctl_home = bentoctl.operator.utils._get_bentoctl_home()
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
    assert bentoctl.operator.utils.git._is_git_link(git_link) is truth


@pytest.mark.parametrize(
    "github_repo, truth",
    [
        ("bentoml/sagemaker", True),
        ("bentoml/aws-lambda:test", True),
        ("notgitrepo", False),
    ],
)
def test_is_github_repo(github_repo, truth):
    assert bentoctl.operator.utils.git._is_github_repo(github_repo) is truth


@pytest.mark.parametrize(
    "official_op, truth", [("aws-lambda", True), ("testop", False)]
)
def test_is_official_operator(official_op, truth):
    assert bentoctl.operator.utils._is_official_operator(official_op) is truth


def test_get_operator_dir_path(tmp_path):
    os.environ["BENTOCTL_HOME"] = str(tmp_path)
    op_dir = bentoctl.operator.utils._get_operator_dir_path(operator_name="test_operator")
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


def test_clone_git_repo(monkeypatch):
    monkeypatch.setattr(operator_utils, "Repo", PatchedRepo)
    repo_path = bentoctl.operator.utils.git._clone_git_repo("git_url")
    assert os.path.exists(repo_path)

    # checkout with branch
    repo_path = bentoctl.operator.utils.git._clone_git_repo("git_url", branch="test")
    assert os.path.exists(repo_path)
    assert os.path.exists(os.path.join(repo_path, "test"))


@pytest.mark.parametrize(
    "github_link, info, raise_error",
    [
        ("bentoml/sagemaker", ("bentoml", "sagemaker", None), False),
        ("bentoml/sagemaker:test", ("bentoml", "sagemaker", "test"), False),
        ("not_github_info", ("bentoml", "sagemaker", "test"), True),
    ],
)
def test_fetch_github_info(github_link, info, raise_error):
    if raise_error:
        with pytest.raises(ValueError):
            bentoctl.operator.utils.git._fetch_github_info(github_link)
    else:
        returned_info = bentoctl.operator.utils.git._fetch_github_info(github_link)
        assert returned_info == info
