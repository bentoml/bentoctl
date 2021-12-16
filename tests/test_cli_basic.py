# pylint: disable=W0621
import os

import pytest
from click.testing import CliRunner

from bentoctl import deployment_config
from bentoctl.cli import bentoctl
from bentoctl.operator import get_local_operator_registry

from .conftest import TESTOP_PATH

TEST_DEPLOYMENT_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "test_deployment_config.yaml"
)


@pytest.fixture
def op_reg_with_testop(tmp_path, monkeypatch):
    op_reg_path = tmp_path / "operator_registry"

    # patch get_bento_path
    monkeypatch.setattr(deployment_config, "get_bento_path", lambda x: x)

    # patched operator registry with testop added
    os.environ["BENTOCTL_HOME"] = str(op_reg_path)
    op_reg = get_local_operator_registry()
    op_reg.add(TESTOP_PATH)
    monkeypatch.setattr(deployment_config, "local_operator_registry", op_reg)

    yield op_reg

    del os.environ["BENTOCTL_HOME"]


def test_cli_deploy(op_reg_with_testop):  # pylint: disable=W0613
    runner = CliRunner()
    result = runner.invoke(
        bentoctl,
        ["deploy", "-f", TEST_DEPLOYMENT_CONFIG_PATH],
    )
    assert result.exit_code == 0
    assert "testdeployment" in result.output


def test_cli_describe(op_reg_with_testop):  # pylint: disable=W0613
    runner = CliRunner()
    result = runner.invoke(bentoctl, ["describe", "-f", TEST_DEPLOYMENT_CONFIG_PATH])
    assert result.exit_code == 0
    assert "testdeployment" in result.output


def test_cli_delete(op_reg_with_testop):  # pylint: disable=W0613
    runner = CliRunner()
    result = runner.invoke(
        bentoctl, ["delete", "-f", TEST_DEPLOYMENT_CONFIG_PATH, "--assume-yes"]
    )
    assert result.exit_code == 0
    assert "testdeployment" in result.output


def test_cli_update(op_reg_with_testop):  # pylint: disable=W0613
    runner = CliRunner()
    result = runner.invoke(bentoctl, ["update", "-f", TEST_DEPLOYMENT_CONFIG_PATH])
    assert result.exit_code == 0
    assert "testdeployment" in result.output
