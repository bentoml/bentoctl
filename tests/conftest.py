# pylint: disable=W0621
import os
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from bentoctl.operator import get_local_operator_registry
from bentoctl.operator.registry import OperatorRegistry

TESTOP_PATH = os.path.join(os.path.dirname(__file__), "test-operator")


@pytest.fixture(scope="function", name="change_test_dir")
def fixture_change_test_dir(request: pytest.FixtureRequest):
    os.chdir(request.fspath.dirname)  # type: ignore (bad pytest stubs)
    yield request.fspath.dirname  # type: ignore (bad pytest stubs)
    os.chdir(request.config.invocation_dir)  # type: ignore (bad pytest stubs)


@pytest.fixture
def mock_operator_registry(tmp_path):
    os.environ["BENTOCTL_HOME"] = str(tmp_path)
    op_reg = get_local_operator_registry()

    yield op_reg

    del os.environ["BENTOCTL_HOME"]


@pytest.fixture
def get_mock_operator_registry(monkeypatch, tmp_path):
    operator_registry = OperatorRegistry(tmp_path)
    monkeypatch.setattr(
        "bentoctl.operator.get_local_operator_registry", lambda: operator_registry
    )
    return operator_registry


@pytest.fixture
def tmp_bento_path(tmpdir):
    Path(tmpdir, "bento.yaml").touch()
    return tmpdir


@pytest.fixture()
def mock_operator():
    @dataclass
    class MockOperator:
        name: str
        schema: dict
        module_name: str = None
        default_template: str = None
        available_templates: list = field(default_factory=lambda: ["terraform"])

        def __post_init__(self):
            if self.module_name is None:
                self.module_name = self.name
            if self.default_template is None:
                self.default_template = self.available_templates[0]

        def generate(self):
            pass

    def factory(**kwargs):
        return MockOperator(**kwargs)

    return factory
