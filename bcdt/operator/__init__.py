import sys
from pathlib import Path

from bcdt.exceptions import OperatorLoadException


def _import_module(name, path):
    import importlib.util
    from importlib.abc import Loader

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert isinstance(spec.loader, Loader)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Operator:
    def __init__(self, path):
        self.path = Path(path)
        if not self.path.is_dir():
            raise ValueError("path should be a valid directory")

        # load the operator
        try:
            self.operator = _import_module(self.path.name, self.path / "__init__.py")
        except Exception as e:
            raise OperatorLoadException(f"Failed to load operator - {e}")

    @property
    def name(self):
        return self.operator.OPERATOR_NAME

    @property
    def operator_schema(self):
        return self.operator.OPERATOR_SCHEMA

    def update(self, bento_path, deployment_name, config_dict):
        d_path = self.operator.update(bento_path, deployment_name, config_dict)

        return d_path

    def deploy(self, bento_path, deployment_name, config_dict):
        d_path = self.operator.deploy(bento_path, deployment_name, config_dict)
        return d_path

    def describe(self, deployment_name, config_dict):
        info_json = self.operator.describe(deployment_name, config_dict)
        return info_json

    def delete(self, deployment_name, config_dict):
        self.operator.delete(deployment_name, config_dict)
