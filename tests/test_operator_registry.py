# pylint: disable=W0621
import json
import os
import shutil
from pathlib import Path

import pytest

from bentoctl.exceptions import OperatorExists, OperatorNotFound
from bentoctl.operator import registry, utils
from bentoctl.operator.operator import Operator

from .conftest import TESTOP_PATH

TEST_OPERATOR = Operator(TESTOP_PATH)


@pytest.fixture
def op_reg(tmp_path):
    os.environ["BENTOCTL_HOME"] = str(tmp_path)
    utils._get_bentoctl_home()
    op_reg = registry.OperatorRegistry(tmp_path / "operators")
    yield op_reg


def test_registry_get(op_reg):
    op_reg.add(TESTOP_PATH)
    testop = op_reg.get("testop")
    assert testop.name == "testop"


def test_registry_init_and_list(tmp_path):
    op_reg = registry.OperatorRegistry(tmp_path)
    assert op_reg.list() == {}

    sample_op_list_json = {"test-operator": {}}

    (tmp_path / "operator_list.json").write_text(json.dumps(sample_op_list_json))
    op_reg = registry.OperatorRegistry(tmp_path)
    assert op_reg.list() == sample_op_list_json


def test_registry_add_local_operator(op_reg):
    op_reg_path = op_reg.path
    assert not (op_reg_path / TEST_OPERATOR.name).exists()
    op_reg.add(TESTOP_PATH)
    assert not (op_reg_path / TEST_OPERATOR.name).exists()
    assert op_reg.operators_list[TEST_OPERATOR.name] == {
        "path": TESTOP_PATH,
        "git_url": None,
        "git_branch": None,
        "is_local": True,
    }

    with pytest.raises(OperatorExists):
        op_reg.add(TESTOP_PATH)


@pytest.mark.parametrize(
    "user_input, git_url, git_branch",
    [
        ("aws-lambda", "https://github.com/bentoml/aws-lambda-deploy.git", "main"),
        ("bentoml/heroku", "https://github.com/bentoml/heroku.git", None),
        (
            "owner/heroku:branch",
            "https://github.com/owner/heroku.git",
            "branch",
        ),
        (
            "https://github.com/bentoml/aws-sagemaker-deploy.git",
            "https://github.com/bentoml/aws-sagemaker-deploy.git",
            None,
        ),
    ],
)
def test_registry_add(user_input, git_url, git_branch, op_reg, monkeypatch):
    def patched_clone_git_repo(git_url, branch=None):  # pylint: disable=W0613
        return TESTOP_PATH

    monkeypatch.setattr(registry, "_clone_git_repo", patched_clone_git_repo)

    op_reg.add(user_input)
    assert (op_reg.path / TEST_OPERATOR.name).exists()
    assert op_reg.operators_list[TEST_OPERATOR.name] == {
        "path": str(op_reg.path / TEST_OPERATOR.name),
        "git_url": git_url,
        "git_branch": git_branch,
        "is_local": False,
    }


def test_registry_update_local_operator(op_reg, tmpdir):
    tmp_testop_path = os.path.join(tmpdir, "testop")
    shutil.copytree(TESTOP_PATH, tmp_testop_path)
    op_reg.add(tmp_testop_path)
    path_to_first_file_before_updation = op_reg.get(TEST_OPERATOR.name).path

    # create new file
    Path(tmp_testop_path, "new_file").touch()
    op_reg.update(TEST_OPERATOR.name)
    path_to_first_file_after_updation = op_reg.get(TEST_OPERATOR.name).path

    assert (op_reg.get(TEST_OPERATOR.name).path / "new_file").exists()
    assert path_to_first_file_before_updation == path_to_first_file_after_updation


def test_registry_update_git_url(op_reg, monkeypatch, tmpdir):
    tmp_testop_path = os.path.join(tmpdir, "testop")
    shutil.copytree(TESTOP_PATH, tmp_testop_path)

    def patched_clone_git_repo(git_url, branch=None):  # pylint: disable=W0613
        return tmp_testop_path

    monkeypatch.setattr(registry, "_clone_git_repo", patched_clone_git_repo)
    op_reg.add("aws-lambda")
    path_to_first_file_before_updation = op_reg.get(TEST_OPERATOR.name).path

    # create new file
    Path(tmp_testop_path, "new_file").touch()

    op_reg.update(TEST_OPERATOR.name)
    path_to_first_file_after_updation = op_reg.get(TEST_OPERATOR.name).path

    assert (op_reg.get(TEST_OPERATOR.name).path / "new_file").exists()
    assert path_to_first_file_before_updation == path_to_first_file_after_updation


def test_registry_remove(op_reg):
    op_reg.add(TESTOP_PATH)
    testop_path = op_reg.path / "testop"

    assert "testop" in op_reg.list()
    op_reg.remove("testop")
    assert "testop" not in op_reg.list()
    assert not testop_path.exists()

    with pytest.raises(OperatorNotFound):
        op_reg.remove("operator_that_is_not_present")
