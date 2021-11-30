import copy
import os
import typing as t
from pathlib import Path

import cerberus
import click
import yaml
import bentoml

from bentoctl.exceptions import DeploymentSpecNotFound, InvalidDeploymentSpec
from bentoctl.operator import get_local_operator_registry
from bentoctl.operator.constants import YATAI_OPERATOR_NAME

metadata_schema = {
    "name": {"required": True, "help_message": "The name for the deployment"},
    "operator": {"required": True},
}

local_operator_registry = get_local_operator_registry()


def get_bento_path(bento: t.Union[str, Path]):
    try:
        bento = bentoml.get(bento)
        return bento.path
    except bentoml.exceptions.NotFound as e:
        if os.path.exists(bento):
            return Path(bento)
        else:
            raise InvalidDeploymentSpec("Bento not found!")


def remove_help_message(schema):
    for field, rules in schema.items():
        if "help_message" in rules:
            del rules["help_message"]
        if rules["type"] == "dict":
            rules["schema"] = remove_help_message(rules["schema"])
        elif rules["type"] == "list":
            rules["schema"] = remove_help_message({"list_item": rules["schema"]})[
                'list_item'
            ]
        schema[field] = rules
    return schema


class DeploymentConfig:
    def __init__(self, deployment_spec: t.Dict[str, t.Any]):
        # currently there is only 1 version for config
        if not deployment_spec["api_version"] == "v1":
            raise InvalidDeploymentSpec("api_version should be 'v1'.")

        self.deployment_spec = deployment_spec
        self.metadata = copy.deepcopy(deployment_spec["metadata"])
        self.operator_spec = copy.deepcopy(deployment_spec["spec"])

        # check `name`
        self.deployment_name = self.metadata.get("name")
        if self.deployment_name is None:
            raise InvalidDeploymentSpec("name not found")

        # check `operator`
        self.operator_name = self.metadata.get("operator")
        if (
            self.operator_name is None
            or self.operator_name not in local_operator_registry.operators_list
        ):
            raise InvalidDeploymentSpec("operator not found")

        # check `bento`
        if self.operator_name is not YATAI_OPERATOR_NAME:
            self.bento = self.operator_spec.pop("bento")
            self.bento_path = get_bento_path(self.bento)

    @classmethod
    def from_file(cls, file_path: t.Union[str, Path]):
        file_path = Path(file_path)
        if not file_path.exists():
            raise DeploymentSpecNotFound
        elif file_path.suffix in [".yaml", ".yml"]:
            try:
                config_dict = yaml.safe_load(file_path.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                raise InvalidDeploymentSpec(exc=e)
        else:
            raise InvalidDeploymentSpec

        return cls(config_dict)

    def validate_operator_spec(self, operator_schema):
        """
        validate the schema using cerberus and show errors properly.
        """
        # cleanup operator_schema by removing 'help_message' field
        operator_schema = remove_help_message(schema=operator_schema)
        v = cerberus.Validator()
        validated_spec = v.validated(self.operator_spec, schema=operator_schema)
        if validated_spec is None:
            raise InvalidDeploymentSpec(spec_errors=v.errors)

        return validated_spec

    def save(self, save_path, filename="deployment_spec.yaml"):
        overide = False
        spec_path = Path(save_path, filename)

        if spec_path.exists():
            overide = click.confirm("deployment spec file exists! Should I overide?")
        if overide:
            spec_path.unlink()
        else:
            return spec_path

        with open(spec_path, "w", encoding="utf-8") as f:
            yaml.dump(self.deployment_spec, f)

        return spec_path
