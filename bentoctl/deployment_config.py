import copy
import logging
import os
import typing as t
from pathlib import Path

import bentoml
import cerberus
import click
import yaml

from bentoctl.exceptions import (
    DeploymentConfigNotFound,
    InvalidDeploymentConfig,
    OperatorNotFound,
)
from bentoctl.operator import get_local_operator_registry
from bentoctl.operator.utils import _is_official_operator

logger = logging.getLogger(__name__)
local_operator_registry = get_local_operator_registry()


def operator_exists(field, operator_name, error):
    available_operators = list(local_operator_registry.list().keys())
    if operator_name not in available_operators:
        error(
            field,
            f"{operator_name} not in list of available operators {available_operators}",
        )


metadata_schema = {
    "name": {"required": True, "help_message": "The name for the deployment"},
    "operator": {
        "required": True,
        "help_message": "The operator to use for deployment",
        "check_with": operator_exists,
    },
}


def get_bento_path(bento_name_or_path: str):
    if os.path.isdir(bento_name_or_path) and os.path.isfile(
        os.path.join(bento_name_or_path, "bento.yaml")
    ):
        return os.path.abspath(bento_name_or_path)
    else:
        try:
            bento = bentoml.get(bento_name_or_path)
            return bento.path
        except bentoml.exceptions.BentoMLException:
            raise InvalidDeploymentConfig(f"Bento {bento_name_or_path} not found!")


def remove_help_message(schema):
    for field, rules in schema.items():
        if "help_message" in rules:
            del rules["help_message"]
        if rules["type"] == "dict":
            rules["schema"] = remove_help_message(rules["schema"])
        elif rules["type"] == "list":
            rules["schema"] = remove_help_message({"list_item": rules["schema"]})[
                "list_item"
            ]
        schema[field] = rules
    return schema


class DeploymentConfig:
    def __init__(self, deployment_config: t.Dict[str, t.Any]):
        # currently there is only 1 version for config
        if not deployment_config.get("api_version") == "v1":
            raise InvalidDeploymentConfig("api_version should be 'v1'.")

        self.deployment_config = deployment_config
        self.metadata = copy.deepcopy(deployment_config.get("metadata"))
        if self.metadata is None:
            raise InvalidDeploymentConfig("'metadata' not found in deployment_config")

        self._set_name()
        self._set_operator()
        self._set_bento()
        self._set_operator_spec()

    @classmethod
    def from_file(cls, file_path: t.Union[str, Path]):
        file_path = Path(file_path)
        if not file_path.exists():
            raise DeploymentConfigNotFound
        elif file_path.suffix in [".yaml", ".yml"]:
            try:
                config_dict = yaml.safe_load(file_path.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                raise InvalidDeploymentConfig(exc=e)
        else:
            raise InvalidDeploymentConfig

        return cls(config_dict)

    def save(self, save_path, filename="deployment_config.yaml"):
        overwrite = False
        config_path = Path(save_path, filename)

        if config_path.exists():
            overwrite = click.confirm(
                "deployment config file exists! Should I overwrite it?"
            )
        if overwrite:
            config_path.unlink()
        else:
            return config_path

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.deployment_config, f)

        return config_path

    def _set_name(self):
        self.deployment_name = self.metadata.get("name")
        if self.deployment_name is None:
            raise InvalidDeploymentConfig("name not found")

    def _set_operator(self):
        self.operator_name = self.metadata.get("operator")
        if self.operator_name is None:
            raise InvalidDeploymentConfig("operator is a required field")
        try:
            self.operator = local_operator_registry.get(self.operator_name)
        except OperatorNotFound:
            if not _is_official_operator(self.operator_name):
                raise InvalidDeploymentConfig(
                    f"operator {self.operator_name} not found in local registry"
                )
            else:
                logger.warning("Install operator %s from bentoml", self.operator_name)
                local_operator_registry.add(self.operator_name)
                self.operator = local_operator_registry.get(self.operator_name)

    def _set_bento(self):
        self.bento = self.deployment_config["spec"].get("bento")
        if self.bento is not None:
            self.bento_path = get_bento_path(self.bento)
        else:
            raise InvalidDeploymentConfig("'bento' not provided in deployment_config")

    def _set_operator_spec(self):
        # cleanup operator_schema by removing 'help_message' field
        operator_schema = remove_help_message(schema=self.operator.operator_schema)
        copied_operator_spec = copy.deepcopy(self.deployment_config["spec"])
        del copied_operator_spec["bento"]
        v = cerberus.Validator()
        validated_spec = v.validated(copied_operator_spec, schema=operator_schema)
        if validated_spec is None:
            raise InvalidDeploymentConfig(config_errors=v.errors)
        self.operator_spec = validated_spec
