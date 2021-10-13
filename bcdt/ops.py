from .plugin_loader import Plugin
from .plugin_manager import get_plugin_list
from .config_manager import load_json_config, build_config_dict

from rich.pretty import pprint


def load_plugin(plugin_name):
    try:
        plugin_path = get_plugin_list()[plugin_name]
    except KeyError:
        print(
            f"the plugin {plugin_name} is not added. Please run 'bcdt plugin list' "
            "to get the list of all the plugin available."
        )
    return Plugin(plugin_path)


def deploy_bundle(bento_bundle, **configs):
    deployment_configs = build_config_dict(configs)
    plugin = load_plugin(deployment_configs["plugin_name"])
    plugin.deploy(
        bento_bundle,
        deployment_configs["deployment_name"],
        deployment_configs["config_dict"],
    )


def update_deployment(bento_bundle, name, **configs):
    deployment_configs = build_config_dict(configs)
    plugin = load_plugin(deployment_configs["plugin_name"])
    plugin.update(
        bento_bundle,
        deployment_configs["deployment_name"],
        deployment_configs["config_dict"],
    )


def describe_deployment(**configs):
    deployment_configs = build_config_dict(configs)
    plugin = load_plugin(deployment_configs["plugin_name"])
    info_json = plugin.describe(
        deployment_configs["deployment_name"], deployment_configs["config_dict"]
    )
    pprint(info_json)


def delete_deployment(**configs):
    deployment_configs = build_config_dict(configs)
    plugin = load_plugin(deployment_configs["plugin_name"])
    plugin.delete(
        deployment_configs["deployment_name"], deployment_configs["config_dict"]
    )
