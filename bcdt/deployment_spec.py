import json
import os
import typing as t
from pathlib import Path

import cerberus
import click
import yaml

from bcdt.exceptions import DeploymentSpecNotFound, InvalidDeploymentSpec
from bcdt.operator import LocalOperatorManager


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

        metadata = deployment_spec["metadata"]

        # check `bento`
        self.bundle_path = load_bento(metadata.get("bento"))

        # check `operator`
        if metadata.get("operator") not in LocalOperatorManager.list():
            raise InvalidDeploymentSpec("operator not found")
        self.operator_name = metadata.get("operator")

        # check `name`
        self.deployment_name = metadata.get("name")
        if self.deployment_name is None:
            raise InvalidDeploymentSpec("name not found")

        self.deployment_spec = deployment_spec

    @classmethod
    def from_file(cls, file_path: t.Union[str, Path]):
        file_path = Path(file_path)
        try:
            if not file_path.exists():
                raise DeploymentSpecNotFound
            if file_path.suffix == ".json":
                config_dict = json.loads(file_path.read_text())
            elif file_path.suffix in [".yaml", ".yml"]:
                config_dict = yaml.safe_load(file_path.read_text())
            else:
                # todo: make it its own exception
                raise InvalidDeploymentSpec
        # catch exceptions for invalid yaml and json config files
        except Exception:
            raise

        return cls(config_dict)

    def validate_operator_spec(self, operator_schema):
        """
        validate the schema using cerberus and show errors properly.
        """
        v = cerberus.Validator()
        validated_spec = v.validated(
            self.deployment_spec["spec"], schema=operator_schema
        )
        if validated_spec is None:
            raise InvalidDeploymentSpec(v.errors)

        return validated_spec

    def save(self, save_path, filename="deployment_spec.yaml"):
        spec_path = Path(save_path, filename)

        if spec_path.exists():
            overide = click.confirm("deployment spec file exists! Should I overide?")
        if overide:
            spec_path.unlink()
        else:
            return spec_path

        with open(spec_path, "w") as f:
            yaml.dump(self.deployment_spec, f)

        return spec_path
