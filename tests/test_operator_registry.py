import json
import os
import shutil
from functools import partial
from pathlib import Path

import pytest

from bentoctl.exceptions import OperatorExists, OperatorIsLocal
from bentoctl.operator import registry
from bentoctl.operator.operator import Operator

from .conftest import TESTOP_PATH


@pytest.fixture
def op_reg_with_testop(tmp_path):
    op_reg = registry.OperatorRegistry(tmp_path)
    op_reg.add_from_path(TESTOP_PATH)

    assert "testop" in op_reg.operators_list
    yield op_reg


def test_registry_get(op_reg_with_testop):
    testop = op_reg_with_testop.get("testop")
    assert testop.name == "testop"


def test_registry_init_and_list(tmp_path):
    op_reg = registry.OperatorRegistry(tmp_path)
    assert op_reg.list() == {}

    sample_op_list_json = {"test-operator": []}
    (tmp_path / "operator_list.json").write_text(json.dumps(sample_op_list_json))
    op_reg = registry.OperatorRegistry(tmp_path)
    assert op_reg.list() == sample_op_list_json


@pytest.fixture
def op_reg(tmp_path):
    op_reg = registry.OperatorRegistry(tmp_path)
    yield op_reg


@pytest.fixture
def testop():
    yield Operator(TESTOP_PATH)


def test_registry__add_and_get(tmp_path):
    op_reg = registry.OperatorRegistry(tmp_path)
    op = Operator(TESTOP_PATH)

    op_name = op_reg._add(op)
    assert op_name == op.name
    assert op.name in op_reg.list()

    op_from_get = op_reg.get(op.name)
    assert op_from_get.path == op.path
    assert op_from_get.git_url is None

    with pytest.raises(OperatorExists):
        op_reg._add(op)


def test_registry_add_from_path(op_reg, testop):
    op_name = op_reg.add_from_path(TESTOP_PATH)
    assert op_name == testop.name


def patched_clone_operator_repo(tmp_path, _, branch=None):
    temp_operator_repo = Path(shutil.copytree(TESTOP_PATH, tmp_path / "testop"))
    if branch is not None:
        (temp_operator_repo / branch).touch()
    return temp_operator_repo


def test_registry_add_from_git(op_reg, testop, monkeypatch, tmp_path):
    def patched_get_op_dir_path(op_name):
        return op_reg.path / op_name

    monkeypatch.setattr(registry, "_get_operator_dir_path", patched_get_op_dir_path)
    monkeypatch.setattr(
        registry,
        "clone_operator_repo",
        partial(patched_clone_operator_repo, tmp_path),
    )

    # without branch
    op_name = op_reg.add_from_git(TESTOP_PATH)
    op = op_reg.get(op_name)
    assert op.name == testop.name
    assert op.path == patched_get_op_dir_path(testop.name)
    assert op.git_url is not None
    assert op.git_url == TESTOP_PATH
    op_reg.remove(testop.name, delete_from_disk=True)

    # with branching
    op_name = op_reg.add_from_git(TESTOP_PATH, "test")
    op = op_reg.get(op_name)
    assert op.name == testop.name
    assert op.path == patched_get_op_dir_path(testop.name)
    assert op.git_url is not None
    assert op.git_url == TESTOP_PATH
    assert (op.path / "test").exists()
    op_reg.remove(testop.name, delete_from_disk=True)


@pytest.mark.parametrize(
    "github_repo_str, owner, repo, repo_branch",
    [
        ("test/test_repo", "test", "test_repo", None),
        ("test_owner/test_repo:test", "test_owner", "test_repo", "test"),
    ],
)
def test_registry_add_from_github(
    github_repo_str, owner, repo, repo_branch, op_reg, monkeypatch
):
    def patched_add_from_git(_, git_link, branch):
        return (git_link, branch)

    monkeypatch.setattr(registry.OperatorRegistry, "add_from_git", patched_add_from_git)
    git_link, branch = op_reg.add_from_github(github_repo_str)
    assert git_link == f"https://github.com/{owner}/{repo}.git"
    assert branch == repo_branch


def test_registry_remove(op_reg, tmp_path):
    testop_path = shutil.copytree(TESTOP_PATH, tmp_path / "testop")
    op_reg.add_from_path(testop_path)

    assert "testop" in op_reg.list()
    op_reg.remove("testop")
    assert "testop" not in op_reg.list()
    assert testop_path.exists()

    # remove directory also
    op_reg.add_from_path(testop_path)
    assert "testop" in op_reg.list()
    op_reg.remove("testop", delete_from_disk=True)
    assert "testop" not in op_reg.list()
    assert not testop_path.exists()


def test_registry_update(op_reg, monkeypatch, tmp_path):
    op = Operator(TESTOP_PATH)
    # git_url is set to TESTOP_PATH for mock Repo to use.
    op_with_url = Operator(TESTOP_PATH, TESTOP_PATH)
    op_reg._add(op)

    with pytest.raises(OperatorIsLocal):
        op_reg.update(op.name)
    op_reg.remove(op.name)

    op_reg._add(op_with_url)
    monkeypatch.setattr(
        registry, "clone_operator_repo", partial(patched_clone_operator_repo, tmp_path)
    )
    path_before_updation = op_reg.get("testop").path
    creation_time = os.path.getctime(path_before_updation)
    op_reg.update("testop")
    path_after_updation = op_reg.get("testop").path
    updation_time = os.path.getctime(path_after_updation)
    assert updation_time > creation_time
    assert path_before_updation == path_after_updation
