from .plugin_mng import load_plugin_action
from .config_mng import load_json_config

from rich.pretty import pprint


def deploy_bundle(bento_bundle, name, config, plugin):
    config_json = load_json_config(config_path=config)
    plugin = load_plugin_action(plugin)
    plugin.deploy(bento_bundle, name, config_json)


def update_deployment(bento_bundle, name, config, plugin):
    config_json = load_json_config(config_path=config)
    plugin = load_plugin_action(plugin)
    plugin.update(bento_bundle, name, config_json)


def describe_deployment(name, config, plugin):
    config_json = load_json_config(config_path=config)
    plugin = load_plugin_action(plugin)
    info_json = plugin.describe(name, config_json)
    pprint(info_json)


def delete_deployment(name, config, plugin):
    config_json = load_json_config(config_path=config)
    plugin = load_plugin_action(plugin)
    plugin.delete(name, config_json)
