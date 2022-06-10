# pylint: disable=W0621
import json
import os
import shutil
from pathlib import Path

import pytest

from bentoctl.exceptions import OperatorExists, OperatorNotFound
from bentoctl.operator import registry
from bentoctl.operator.operator import Operator
from tests.conftest import TESTOP_PATH

TEST_OPERATOR = Operator(TESTOP_PATH)


@pytest.fixture
def op_reg(tmp_path):
    os.environ["BENTOCTL_HOME"] = str(tmp_path)
    op_reg = registry.OperatorRegistry(tmp_path)
    yield op_reg


def test_registry_get(op_reg):
    op_reg.install_operator(TESTOP_PATH)
    testop = op_reg.get("testop")
    assert testop.name == "testop"


def test_registry_init_and_list(tmp_path):
    op_reg = registry.OperatorRegistry(tmp_path)
    assert op_reg.list() == {}

    sample_op_list_json = {"test-operator": {}}

    (tmp_path / "operator_list.json").write_text(json.dumps(sample_op_list_json))
    op_reg = registry.OperatorRegistry(tmp_path)
    assert op_reg.list() == sample_op_list_json


def test_registry_install_local_operator(op_reg):
    op_reg_path = op_reg.path
    assert not (op_reg_path / TEST_OPERATOR.name).exists()
    op_reg.install_operator(TESTOP_PATH)
    assert not (op_reg_path / TEST_OPERATOR.name).exists()
    assert op_reg.operators_list[TEST_OPERATOR.name] == {
        "path": TESTOP_PATH,
        "is_official": False,
        "is_local": True,
        "version": None,
    }

    with pytest.raises(OperatorExists):
        op_reg.install_operator(TESTOP_PATH)


def test_registry_update_local_operator(op_reg, tmpdir):
    tmp_testop_path = os.path.join(tmpdir, "testop")
    shutil.copytree(TESTOP_PATH, tmp_testop_path)
    op_reg.install_operator(tmp_testop_path)
    path_to_first_file_before_updation = op_reg.get(TEST_OPERATOR.name).path

    # create new file
    Path(tmp_testop_path, "new_file").touch()
    op_reg.update_operator(TEST_OPERATOR.name)
    path_to_first_file_after_updation = op_reg.get(TEST_OPERATOR.name).path

    assert (op_reg.get(TEST_OPERATOR.name).path / "new_file").exists()
    assert path_to_first_file_before_updation == path_to_first_file_after_updation


def test_registry_remove(op_reg):
    op_reg.install_operator(TESTOP_PATH)
    testop_path = op_reg.path / "testop"

    assert "testop" in op_reg.list()
    op_reg.remove_operator("testop")
    assert "testop" not in op_reg.list()
    assert not testop_path.exists()

    with pytest.raises(OperatorNotFound):
        op_reg.remove_operator("operator_that_is_not_present")
