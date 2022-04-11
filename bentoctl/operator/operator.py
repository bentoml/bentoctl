import importlib
import logging
import os
import subprocess
import sys
from pathlib import Path

from bentoctl.exceptions import (
    OperatorConfigNotFound,
    OperatorLoadException,
    PipInstallException,
)
from bentoctl.utils import console

logger = logging.getLogger(__name__)


class Operator:
    def __init__(self, path):
        self.path = Path(path)

        # load the operator config
        if not os.path.exists(os.path.join(self.path, "operator_config.py")):
            raise OperatorConfigNotFound(operator_path=self.path)

        self.operator_config = _import_module("operator_config", self.path)

    @property
    def name(self):
        return self.operator_config.OPERATOR_NAME

    @property
    def module_name(self):
        if hasattr(self.operator_config, "OPERATOR_MODULE"):
            return self.operator_config.OPERATOR_MODULE
        else:
            self.self.operator_name

    @property
    def schema(self):
        return self.operator_config.OPERATOR_SCHEMA

    @property
    def default_template(self):
        return self.operator_config.OPERATOR_DEFAULT_TEMPLATE

    @property
    def available_templates(self):
        if hasattr(self.operator_config, "OPERATOR_AVAILABLE_TEMPLATES"):
            return self.operator_config.OPERATOR_AVAILABLE_TEMPLATES
        else:
            return [self.operator_config.OPERATOR_DEFAULT_TEMPLATE]

    def generate(self, name, spec, template_type, destination_dir, values_only=True):
        operator = self._load_operator_module()
        return operator.generate(
            name, spec, template_type, destination_dir, values_only
        )

    def create_deployable(
        self, bento_path, destination_dir, bento_metadata, overwrite_deployable
    ):
        operator = self._load_operator_module()
        return operator.create_deployable(
            bento_path, destination_dir, bento_metadata, overwrite_deployable
        )

    def get_registry_info(self, deployment_name, operator_spec):
        operator = self._load_operator_module()
        return operator.get_registry_info(deployment_name, operator_spec)

    def install_dependencies(self):
        requirement_txt_filepath = os.path.join(self.path, "requirements.txt")
        if not os.path.exists(requirement_txt_filepath):
            logger.info(
                "requirements.txt not found in Operator, skipping installation of "
                "dependencies"
            )
            return
        with console.status("Installing dependencies from requirements.txt"):
            completedprocess = subprocess.run(
                ["pip", "install", "-r", requirement_txt_filepath],
                capture_output=True,
                check=False,
            )
        if completedprocess.returncode == 0:  # success
            logger.info(completedprocess.stdout.decode("utf-8"))
        else:
            logger.error(completedprocess.stderr.decode("utf-8"))
            raise PipInstallException(stderr=completedprocess.stderr.decode("utf-8"))

    def _load_operator_module(self):
        return _import_module(self.module_name, self.path)


def _import_module(module_name, path):
    try:
        sys.path.insert(0, os.path.abspath(path))
        module = importlib.import_module(module_name)
        return module
    except (ImportError, ModuleNotFoundError) as e:
        logger.exception(e)
        raise OperatorLoadException(f"Failed to load module {module_name} - {e}.")
