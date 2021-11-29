from pathlib import Path

import pytest

from bentoctl import deployment_spec as dspec
from bentoctl.operator import OperatorRegistry
from bentoctl.exceptions import InvalidDeploymentSpec, DeploymentSpecNotFound
from bentoctl.operator.operator import _import_module

from .conftest import TESTOP_PATH


def test_load_bento(tmp_path: Path):
    tmp_bento_path = tmp_path / "testbento"

    with pytest.raises(InvalidDeploymentSpec):
        dspec.load_bento(tmp_bento_path)

    tmp_bento_path.mkdir()
    assert dspec.load_bento(tmp_bento_path) == tmp_bento_path


def assert_no_help_message_in_schema(schema):
    for _, rules in schema.items():
        assert "help_message" not in rules
        if rules["type"] == "dict":
            assert_no_help_message_in_schema(rules["schema"])
        elif rules["type"] == "list":
            assert_no_help_message_in_schema({"list_item": rules["schema"]})


def test_remove_help_message():
    operator_config = _import_module("operator_config", TESTOP_PATH)
    schema = operator_config.OPERATOR_SCHEMA
    schema_without_help_msg = dspec.remove_help_message(schema)
    assert_no_help_message_in_schema(schema_without_help_msg)


def test_deployment_spec_init(op_reg, monkeypatch):
    # empty deployment_spec
    with pytest.raises(InvalidDeploymentSpec):
        dspec.DeploymentSpec({})

    # deployment_spec with incorrect api_version
    with pytest.raises(InvalidDeploymentSpec):
        dspec.DeploymentSpec({"api_version": "v1"})

    # deployment_spec with no deployment name
    with pytest.raises(InvalidDeploymentSpec):
        dspec.DeploymentSpec({"api_version": "v1", "metadata": {}, "spec": {}})

    # deployment_spec with operator that is not installed
    monkeypatch.setattr(dspec, "local_operator_registry", op_reg)
    with pytest.raises(InvalidDeploymentSpec):
        dspec.DeploymentSpec(
            {
                "api_version": "v1",
                "metadata": {"name": "test", "operator": "testop"},
                "spec": {},
            }
        )

    # deployment_spec is added
    op_reg.add(TESTOP_PATH)
    assert dspec.DeploymentSpec(
        {
            "api_version": "v1",
            "metadata": {"name": "test", "operator": "testop"},
            "spec": {},
        }
    )

    # valid bento
    dspecobj = dspec.DeploymentSpec(
        {
            "api_version": "v1",
            "metadata": {"name": "test", "operator": "testop"},
            "spec": {"bento": TESTOP_PATH},
        }
    )
    assert dspecobj.bento == TESTOP_PATH
    assert dspecobj.bento_path == Path(TESTOP_PATH)


VALID_YAML = """
api_version: v1
metadata:
    name: test
    operator: testop
spec:
    project_id: testproject
    instances:
        min: 1
        max: 2
"""
INVALID_YAML = """
api_version: tst: something: something
"""
VALID_YAML_INVALID_SCHEMA = """
api_version: v1
metadata:
    name: test
    operator: testop
spec:
    project_id: testproject
"""


def create_yaml_file(yml_str, path):
    with open(Path(path, "deployment_spec.yaml"), "w", encoding="utf-8") as f:
        f.write(yml_str)


@pytest.fixture
def op_reg_with_testop(op_reg, monkeypatch):
    monkeypatch.setattr(dspec, "local_operator_registry", op_reg)
    op_reg.add(TESTOP_PATH)

    yield op_reg


def test_deployment_spec_from_file(tmp_path, op_reg_with_testop):
    with pytest.raises(DeploymentSpecNotFound):
        dspec.DeploymentSpec.from_file(tmp_path / "nofile.yaml")

    create_yaml_file(INVALID_YAML, tmp_path)
    with pytest.raises(InvalidDeploymentSpec):
        dspec.DeploymentSpec.from_file(tmp_path / "deployment_spec.yaml")

    create_yaml_file(VALID_YAML, tmp_path)
    assert dspec.DeploymentSpec.from_file(tmp_path / "deployment_spec.yaml")


def test_validate_operator_spec(op_reg_with_testop):
    operator_config = _import_module("operator_config", TESTOP_PATH)
    schema = operator_config.OPERATOR_SCHEMA

    import yaml
    dspec_obj = dspec.DeploymentSpec(yaml.safe_load(VALID_YAML))
    dspec_obj.validate_operator_spec(schema)

    with pytest.raises(InvalidDeploymentSpec):
        dspec_obj = dspec.DeploymentSpec(yaml.safe_load(VALID_YAML_INVALID_SCHEMA))
        dspec_obj.validate_operator_spec(schema)
