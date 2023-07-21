import copy
import logging
import os
import typing as t
from contextlib import contextmanager
from pathlib import Path

import bentoml
import cerberus
import fs
import fs.mirror
import yaml
from bentoml import Bento
from bentoml.exceptions import NotFound
from bentoml.models import get as get_model

from bentoctl.exceptions import (
    BentoNotFound,
    DeploymentConfigNotFound,
    InvalidDeploymentConfig,
    OperatorNotFound,
)
from bentoctl.operator import get_local_operator_registry
from bentoctl.operator.utils import _is_official_operator
from bentoctl.utils import is_debug_mode

logger = logging.getLogger(__name__)
local_operator_registry = get_local_operator_registry()


def operator_exists(field, operator_name, error):
    available_operators = list(local_operator_registry.list().keys())
    if operator_name not in available_operators:
        error(
            field,
            f"{operator_name} not in list of available operators {available_operators}",
        )


deployment_config_schema = {
    "name": {"required": True, "help_message": "The name for the deployment"},
    "operator": {
        "type": "dict",
        "required": True,
        "schema": {
            "name": {
                "help_message": "The operator to use for deployment",
                "check_with": operator_exists,
            }
        },
    },
    "template": {
        "required": True,
        "default": "terraform",
        "help_message": "The template type for generated deployment",
    },
    "spec": {
        "required": True,
    },
    "env": {
        "required": False,
        "nullable": True,
        "type": "dict",
        "keysrules": {
            "type": "string",
            "regex": "[a-zA-Z_]{1,}[a-zA-Z0-9_]{0,}",
            "help_message": "An environment variable name to set for deployment",
        },
        "valuesrules": {
            "type": "string",
            "help_message": "An environment variable value to set for deployment",
        },
        "help_message": "Used to set runtime environment variables for deployment",
    },
}


def remove_help_message(schema):
    """
    Recursively remove the help_messages from the cerberus schema
    """
    for field, rules in schema.items():
        if not isinstance(rules, dict):
            continue

        if "help_message" in rules:
            del rules["help_message"]
        if rules.get("type") == "dict":
            if "schema" in rules:
                rules["schema"] = remove_help_message(rules.get("schema"))
            for key in ("keysrules", "valuesrules"):
                if key in rules:
                    rules[key] = remove_help_message({key: rules[key]})[key]
        elif rules.get("type") == "list":
            rules["schema"] = remove_help_message(
                {"list_item": rules.get("schema", {})}
            )["list_item"]
        schema[field] = rules
    return schema


def get_bento_metadata(bento_path: str) -> dict:
    metadata = {}

    bento = Bento.from_fs(fs.open_fs(bento_path))
    metadata["tag"] = bento.tag
    metadata["bentoml_version"] = ".".join(bento.info.bentoml_version.split(".")[:3])

    python_version_txt_path = "env/python/version.txt"
    python_version_txt_path = os.path.join(bento_path, python_version_txt_path)
    with open(python_version_txt_path, "r", encoding="utf-8") as f:
        python_version = f.read()
    metadata["python_version"] = ".".join(python_version.split(".")[:2])

    return metadata


class DeploymentConfig:
    def __init__(self, deployment_config: t.Dict[str, t.Any]):
        self.bento = None
        self.repository_name = None

        # currently there is only 1 version for config
        if not deployment_config.get("api_version") == "v1":
            raise InvalidDeploymentConfig("api_version should be 'v1'.")

        self.deployment_config = deployment_config
        self._set_name()
        self._set_operator()
        self._set_template_type()
        self._set_env()
        self._set_operator_spec()

    def _set_name(self):
        self.deployment_name = self.deployment_config.get("name")
        self.repository_name = self.deployment_name
        if self.deployment_name is None:
            raise InvalidDeploymentConfig("name not found")

    def _set_operator(self):
        operator_dict = self.deployment_config.get("operator")
        if operator_dict is None:
            raise InvalidDeploymentConfig("operator is a required field")
        self.operator_name = operator_dict.get("name")
        if self.operator_name is None:
            raise InvalidDeploymentConfig("operator.name is a required field")
        try:
            self.operator = local_operator_registry.get(self.operator_name)
        except OperatorNotFound:
            if not _is_official_operator(self.operator_name):
                raise InvalidDeploymentConfig(
                    f"operator {self.operator_name} not found in local registry"
                )
            else:
                logger.warning("Install operator %s from bentoml", self.operator_name)
                local_operator_registry.install_operator(self.operator_name)
                self.operator = local_operator_registry.get(self.operator_name)

    def _set_template_type(self):
        self.template_type = self.deployment_config.get("template")
        if self.template_type is None:
            raise InvalidDeploymentConfig("template is a required field")
        elif self.template_type not in self.operator.available_templates:
            raise InvalidDeploymentConfig(
                (
                    f"template '{self.template_type}' not supported by operator "
                    f"{self.operator_name}. Available template types are "
                    f"{self.operator.available_templates}."
                )
            )

    def _set_env(self):
        copied_env = copy.deepcopy(self.deployment_config.get("env"))
        validated_env = None
        if copied_env is not None:
            v = cerberus.Validator()
            env_schema = remove_help_message(
                {"env": copy.deepcopy(deployment_config_schema["env"])}
            )
            validated_env = v.validated({"env": copied_env}, env_schema)["env"]
            if validated_env is None:
                raise InvalidDeploymentConfig(config_errors=v.errors)
        self.env = validated_env

    def _set_operator_spec(self):
        # cleanup operator_schema by removing 'help_message' field
        operator_schema = remove_help_message(schema=self.operator.schema)
        copied_operator_spec = copy.deepcopy(self.deployment_config["spec"])
        v = cerberus.Validator()
        validated_spec = v.validated(copied_operator_spec, schema=operator_schema)
        if validated_spec is None:
            raise InvalidDeploymentConfig(config_errors=v.errors)

        # We add `env` through the operator spec to avoid introducing an
        # additional argument to every operator which would be a breaking change.
        # TODO: introduce the breaking change to clean up the interface.
        if self.env is not None:
            validated_spec["env"] = self.env

        self.operator_spec = validated_spec

    def set_bento(self, bento_tag: str):
        try:
            self.bento = bentoml.get(bento_tag)
        except NotFound as e:
            raise BentoNotFound(bento_tag) from e

    @classmethod
    def from_file(cls, file_path: t.Union[str, Path]):
        file_path = Path(file_path)
        if not file_path.exists():
            raise DeploymentConfigNotFound(file_path)
        elif file_path.suffix in [".yaml", ".yml"]:
            try:
                config_dict = yaml.safe_load(file_path.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                raise InvalidDeploymentConfig(exc=e)
        else:
            raise InvalidDeploymentConfig

        return cls(config_dict)

    def save(self, save_path, filename="deployment_config.yaml"):
        config_path = os.path.join(save_path, filename)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(
                self.deployment_config, f, default_flow_style=False, sort_keys=False
            )

        return config_path

    def generate(self, destination_dir=os.curdir, values_only=False):
        """
        Generate the template and params file in destination_dir.
        """
        generated_files = self.operator.generate(
            name=self.deployment_name,
            spec=self.operator_spec,
            template_type=self.template_type,
            destination_dir=destination_dir,
            values_only=values_only,
        )

        return generated_files

    @contextmanager
    def _prepare_bento_dir(self) -> t.Generator[str, None, None]:
        assert self.bento is not None
        with fs.open_fs("temp://") as temp_fs, fs.open_fs(self.bento.path) as bento_fs:
            fs.mirror.mirror(bento_fs, temp_fs)
            models_fs = temp_fs.makedirs("models", recreate=True)
            for model_info in self.bento.info.models:
                model = get_model(model_info.tag)
                model_fs = models_fs.makedirs(model_info.tag.path())
                fs.mirror.mirror(model.path, model_fs)
            yield temp_fs.getsyspath("/")

    def create_deployable(self, destination_dir=os.curdir) -> str:
        """
        Creates the deployable in the destination_dir and returns
        the docker args for building
        """
        # NOTE: In the case of debug mode, we want to keep the deployable
        # for debugging purpose. So by setting overwrite_deployable to false,
        # we don't delete the deployable after the build.
        with self._prepare_bento_dir() as bento_path:
            return self.operator.create_deployable(
                bento_path=bento_path,
                destination_dir=destination_dir,
                bento_metadata=get_bento_metadata(bento_path),
                overwrite_deployable=not is_debug_mode(),
            )

    def create_repository(self):
        (
            repository_url,
            username,
            password,
        ) = self.operator.create_repository(
            repository_name=self.repository_name,
            operator_spec=self.operator_spec,
        )
        return repository_url, username, password

    def delete_repository(self):
        return self.operator.delete_repository(self.repository_name, self.operator_spec)

    def generate_docker_image_tag(self, repository_url: str) -> str:
        image_tag = f"{repository_url.replace('https://', '')}:{self.bento.tag.version}"
        self.operator_spec["image_tag"] = image_tag
        return image_tag

    def generate_local_image_tag(self) -> str:
        image_tag = (
            f"{self.operator_name}-{self.bento.tag.name}:{self.bento.tag.version}"
        )
        return image_tag
