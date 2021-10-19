import sys
import os
from pathlib import Path


def import_module(name, path):
    import importlib.util
    from importlib.abc import Loader

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert isinstance(spec.loader, Loader)
    spec.loader.exec_module(module)
    return module


class Operator:
    def __init__(self, path):
        self.path = Path(path)
        if not self.path.is_dir():
            raise ValueError("path should be a valid directory")

        # load the operator
        sys.path.append(os.fspath(path))
        self.operator = import_module("operator", self.path / "__init__.py")
        sys.path.remove(os.fspath(path))

    @property
    def name(self):
        return self.operator.OPERATOR_NAME

    @property
    def default_fields(self):
        return self.operator.DEFAULT_FIELDS

    @property
    def required_fields(self):
        return self.operator.REQUIRED_FIELDS

    def update(self, bento_bundle_path, deployment_name, config_dict):
        d_path = self.operator.update(bento_bundle_path, deployment_name, config_dict)
        return d_path

    def deploy(self, bento_bundle_path, deployment_name, config_dict):
        d_path = self.operator.deploy(bento_bundle_path, deployment_name, config_dict)
        return d_path

    def describe(self, deployment_name, config_dict):
        info_json = self.operator.describe(deployment_name, config_dict)
        return info_json

    def delete(self, deployment_name, config_dict):
        self.operator.delete(deployment_name, config_dict)
