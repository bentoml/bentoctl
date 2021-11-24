import importlib
import os
import sys
from pathlib import Path

from bentoctl.exceptions import OperatorConfigNotFound, OperatorLoadException


class Operator:
    def __init__(self, path):
        self.path = Path(path)

        # load the operator config
        if not os.path.exists(os.path.join(self.path, "operator_config.py")):
            raise OperatorConfigNotFound(operator_path=self.path)
        try:
            operator_config = _import_module("operator_config", self.path)
        except (ImportError, ModuleNotFoundError) as e:
            raise OperatorLoadException(f"Failed to load operator - {e}")

        self.operator_name = operator_config.OPERATOR_NAME
        if hasattr(operator_config, "OPERATOR_MODULE"):
            self.operator_module = operator_config.OPERATOR_MODULE
        else:
            self.operator_module = self.operator_name
        self.operator_schema = operator_config.OPERATOR_SCHEMA

    @property
    def name(self):
        return self.operator_name

    def update(self, bento_path, deployment_name, config_dict):
        operator = _import_module(self.operator_module, self.path)
        d_path = operator.update(bento_path, deployment_name, config_dict)

        return d_path

    def deploy(self, bento_path, deployment_name, config_dict):
        operator = _import_module(self.operator_module, self.path)
        d_path = operator.deploy(bento_path, deployment_name, config_dict)
        return d_path

    def describe(self, deployment_name, config_dict):
        operator = _import_module(self.operator_module, self.path)
        info_json = operator.describe(deployment_name, config_dict)
        return info_json

    def delete(self, deployment_name, config_dict):
        operator = _import_module(self.operator_module, self.path)
        operator.delete(deployment_name, config_dict)


def _import_module(module_name, path):
    sys.path.insert(0, os.path.abspath(path))
    module = importlib.import_module(module_name)
    return module
