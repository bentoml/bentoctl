# pylint: disable=W0621
import os
from pathlib import Path

import pytest

from bentoctl.operator import get_local_operator_registry

TESTOP_PATH = os.path.join(os.path.dirname(__file__), "test-operator")


@pytest.fixture
def op_reg(tmp_path):
    os.environ["BENTOCTL_HOME"] = str(tmp_path)
    op_reg = get_local_operator_registry()

    yield op_reg

    del os.environ["BENTOCTL_HOME"]


@pytest.fixture
def tmp_bento_path(tmpdir):
    Path(tmpdir, "bento.yaml").touch()
    return tmpdir
