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

        operator_config = _import_module("operator_config", self.path)

        self.operator_name = operator_config.OPERATOR_NAME
        if hasattr(operator_config, "OPERATOR_MODULE"):
            self.module_name = operator_config.OPERATOR_MODULE
        else:
            self.module_name = self.operator_name
        self.operator_schema = operator_config.OPERATOR_SCHEMA

    @property
    def name(self):
        return self.operator_name

    def generate(self, *args, **kwargs):
        operator = self._load_operator_module()
        return operator.generate(*args, **kwargs)

    def create_deployable(self, *args, **kwargs):
        operator = self._load_operator_module()
        return operator.create_deployable(*args, **kwargs)

    def get_registry_info(self, *args, **kwargs):
        operator = self._load_operator_module()
        return operator.get_registry_info(*args, **kwargs)

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
