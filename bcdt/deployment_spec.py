import os
import typing as t
from pathlib import Path

import cerberus
import click
import yaml

from bcdt.exceptions import DeploymentSpecNotFound, InvalidDeploymentSpec
from bcdt.operator.manager import LocalOperatorManager

metadata_schema = {
    "name": {"required": True, "help_message": "The name for the deployment"},
    "operator": {"required": True},
}


def load_bento(bundle: t.Union[str, Path]):
    # TODO: hook it up with bento.store and yatai
    if not os.path.exists(bundle):
        raise InvalidDeploymentSpec("bundle not found!")

    return Path(bundle)


class DeploymentSpec:
    def __init__(self, deployment_spec: t.Dict[str, t.Any]):
        # currently there is only 1 version for config
        if not deployment_spec["api_version"] == "v1":
            raise InvalidDeploymentSpec("api_version should be 'v1'.")

        self.deployment_spec = deployment_spec
        self.metadata = deployment_spec["metadata"]
        self.operator_spec = deployment_spec["spec"]

        # check `name`
        self.deployment_name = self.metadata.get("name")
        if self.deployment_name is None:
            raise InvalidDeploymentSpec("name not found")

        # check `operator`
        if self.metadata.get("operator") not in LocalOperatorManager.list():
            raise InvalidDeploymentSpec("operator not found")
        self.operator_name = self.metadata.get("operator")

        # check `bento`
        if "bento" in self.operator_spec:
            self.bento = self.operator_spec.pop("bento")
            self.bento_path = load_bento(self.bento)

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
        v = cerberus.Validator()

        # process operator schema and remove the 'help_message' field
        for _, rules in operator_schema.items():
            if "help_message" in rules:
                rules.pop("help_message")
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
