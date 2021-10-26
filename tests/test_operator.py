import os
import shutil
from functools import partial
from pathlib import Path

import pytest

from bcdt import operator as op

from .conftest import TESTOP_PATH


def test_bcdt_home_dir(tmpdir):

    assert op.manager._get_bcdt_home() == Path(os.path.expanduser("~/bcdt"))

    os.environ["BCDT_HOME"] = tmpdir.dirname
    bcdt_home = op.manager._get_bcdt_home()
    assert bcdt_home == Path(tmpdir.dirname)


def test_operator_loader(tmpdir):
    shutil.copytree(TESTOP_PATH, os.path.join(tmpdir, "testop"))
    operator = op.Operator(os.path.join(tmpdir, "testop"))
    assert operator.name == "testop"

    deployable_path = operator.deploy("test_bundle", "first", {})
    assert os.path.exists(deployable_path)
    shutil.rmtree(deployable_path)
    deployable_path = operator.update("test_bundle", "second", {})
    assert os.path.exists(deployable_path)
    shutil.rmtree(deployable_path)

    assert operator.describe("third", {}) is not None
    assert operator.delete("forth", {}) is None


def test_operator_manager(tmpdir):
    """
    Tests all the functionalities for the OperatorManager obj.
    """
    from bcdt.exceptions import OperatorExists, OperatorNotFound
    from bcdt.operator.manager import OperatorManager

    # brand new manager, there is no `operator_list.json` file in filesystem.
    op_mngr = OperatorManager(tmpdir)
    op_mngr.add("testop", TESTOP_PATH, op_repo_url=None)
    op_mngr.add("testop_with_url", TESTOP_PATH, op_repo_url="testop_url")

    op1 = op_mngr.get("testop")
    assert op1.op_path == TESTOP_PATH
    assert op1.op_repo_url is None
    op2 = op_mngr.get("testop_with_url")
    assert op2.op_path == TESTOP_PATH
    assert op2.op_repo_url == "testop_url"

    # get something that is not present
    with pytest.raises(OperatorNotFound):
        op_mngr.get("op_not_present")

    # add something that exsits
    with pytest.raises(OperatorExists):
        op_mngr.add("testop", TESTOP_PATH)

    # `operator_list.json` is present, init with existing.
    op_mngr = OperatorManager(tmpdir)
    ops_list = op_mngr.list()
    (op1_path, op1_url) = ops_list["testop"]
    assert op1_path == TESTOP_PATH
    assert op1_url is None
    (op2_path, op2_url) = ops_list["testop_with_url"]
    assert op2_path == TESTOP_PATH
    assert op2_url == "testop_url"

    # operator updation
    op_mngr.update("testop", "new_path", "new_url")
    op1_path, op1_url = op_mngr.get("testop")
    assert op1_path == "new_path"
    assert op1_url == "new_url"

    # operator removal
    op_mngr.remove("testop")
    with pytest.raises(OperatorNotFound):
        op_mngr.get("testop")


def test_operator_management_add(tmpdir, monkeypatch):
    """
    Test the operator management operation `add` that adds an operator from the loca
    file system.
    """
    tmpOpsManager = op.manager.OperatorManager(tmpdir.dirname)
    monkeypatch.setattr(op.manager, "LocalOpsManager", tmpOpsManager)

    assert op.manager.add_operator(TESTOP_PATH) == "testop"
    op.manager.remove_operator("testop")


github_url = "https://github.com/{owner}/{name}/archive/{branch}.zip"


@pytest.mark.parametrize(
    ("user_input", "expected_repo_url"),
    [
        (
            "aws-lambda",
            github_url.format(
                owner="jjmachan", name="aws-lambda-deploy", branch="deployers"
            ),
        ),
        (
            "bentoml/aws-sagemaker",
            github_url.format(
                owner="bentoml", name="aws-sagemaker", branch="deployers"
            ),
        ),
        (
            "bentoml/aws-sagemaker:master",
            github_url.format(owner="bentoml", name="aws-sagemaker", branch="master"),
        ),
        (
            "https://github.com/bentoml/google-cloud-run-deploy.git",
            github_url.format(
                owner="bentoml", name="google-cloud-run-deploy", branch="deployers"
            ),
        ),
    ],
)
def test_operator_management_add_with_url(
    tmpdir, monkeypatch, user_input, expected_repo_url
):
    tmpOpsManager = op.manager.OperatorManager(tmpdir.dirname)
    monkeypatch.setattr(op.manager, "LocalOpsManager", tmpOpsManager)

    def _mock_download_repo(repo_url, operator_dir_name, expected_repo_url=None):
        """
        makes a mock function for the _download_repo function in bcdt.operator.manager.
        This mock function has an additional check to ensure the correct URL is
        generated for download.
        """
        assert repo_url == expected_repo_url
        op_dir = Path(tmpdir, operator_dir_name)
        shutil.copytree(TESTOP_PATH, op_dir)
        return op_dir.as_posix()

    monkeypatch.setattr(
        op.manager,
        "_download_repo",
        partial(_mock_download_repo, expected_repo_url=expected_repo_url),
    )
    assert op.manager.add_operator(user_input) == "testop"
    op.manager.remove_operator("testop")


def test_operator_management_update(mock_download_repo):
    op = mock_download_repo
    assert op.manager.add_operator("aws-lambda") == "testop"
    creation_time = os.path.getctime(op.manager.LocalOpsManager.get("testop").op_path)
    op.manager.update_operator("testop")
    updation_time = os.path.getctime(op.manager.LocalOpsManager.get("testop").op_path)
    assert updation_time > creation_time
