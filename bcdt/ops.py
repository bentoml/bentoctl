from .plugin_loader import Plugin
from .plugin_mng import _get_plugin_list
from .config_mng import load_json_config

from rich.pretty import pprint


def load_plugin(plugin_name):
    try:
        plugin_path = _get_plugin_list()[plugin_name]
    except KeyError:
        print(
            f"the plugin {plugin_name} is not added. Please run 'bcdt plugin list' "
            "to get the list of all the plugin available."
        )
    return Plugin(plugin_path)


def deploy_bundle(bento_bundle, name, config, plugin_name):
    config_json = load_json_config(config_path=config)
    plugin = load_plugin(plugin_name)
    plugin.deploy(bento_bundle, name, config_json)


def update_deployment(bento_bundle, name, config, plugin_name):
    config_json = load_json_config(config_path=config)
    plugin = load_plugin(plugin_name)
    plugin.update(bento_bundle, name, config_json)


def describe_deployment(name, config, plugin_name):
    config_json = load_json_config(config_path=config)
    plugin = load_plugin(plugin_name)
    info_json = plugin.describe(name, config_json)
    pprint(info_json)


def delete_deployment(name, config, plugin_name):
    config_json = load_json_config(config_path=config)
    plugin = load_plugin(plugin_name)
    plugin.delete(name, config_json)
