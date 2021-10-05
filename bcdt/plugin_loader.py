import sys
import os
import json
from pathlib import Path


def import_module(name, path):
    import importlib.util
    from importlib.abc import Loader

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert isinstance(spec.loader, Loader)
    spec.loader.exec_module(module)
    return module


class Plugin:
    def __init__(self, path):
        self.path = Path(path)
        if not self.path.is_dir():
            raise ValueError("path should be a valid directory")

        # add plugin path to sys.path (as string) for discoverability
        sys.path.append(os.fspath(path))

    @property
    def name(self):
        return self.path.name

    @property
    def deployment_config(self):
        conf_file = self.path / "deployment_config.json"
        return json.loads(conf_file.read_text())

    def update(self, bento_bundle_path, deployment_name, config_dict):
        updater = import_module("plugin_updater", self.path / "update.py")
        updater.update(bento_bundle_path, deployment_name, config_dict)

    def deploy(self, bento_bundle_path, deployment_name, config_dict):
        deployer = import_module("plugin_deployer", self.path / "deploy.py")
        deployer.deploy(bento_bundle_path, deployment_name, config_dict)

    def describe(self, deployment_name, config_dict):
        describer = import_module("plugin_describer", self.path / "describe.py")
        describer.describe(deployment_name, config_dict)

    def delete(self, deployment_name, config_dict):
        deleter = import_module("plugin_deleter", self.path / "delete.py")
        deleter.delete(deployment_name, config_dict)
