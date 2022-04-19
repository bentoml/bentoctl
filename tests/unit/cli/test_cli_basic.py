# pylint: disable=W0621
import os

import pytest

from bentoctl import deployment_config
from bentoctl.operator import get_local_operator_registry

from tests.conftest import TESTOP_PATH

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
