from .operator_loader import Operator
from .operator_manager import get_operator_list
from .config_manager import build_config_dict
from .deployment_store import localstore

from rich.pretty import pprint


def load_operator(operator_name):
    try:
        operator_path = get_operator_list()[operator_name]
    except KeyError:
        print(
            f"the operator {operator_name} is not added. Please run "
            "'bcdt operator list' to get the list of all the operator available."
        )
        raise KeyError
    return Operator(operator_path)


def deploy_bundle(bento_bundle, **configs):
    deployment_configs = build_config_dict(configs)
    operator = load_operator(deployment_configs["operator_name"])
    deployable_path = operator.deploy(
        bento_bundle,
        deployment_configs["deployment_name"],
        deployment_configs["config_dict"],
    )
    localstore.add(
        deployment_configs["operator_name"],
        deployment_configs["deployment_name"],
        deployable_path,
    )


def update_deployment(bento_bundle, name, **configs):
    deployment_configs = build_config_dict(configs)
    operator = load_operator(deployment_configs["operator_name"])
    deployable_path = operator.update(
        bento_bundle,
        deployment_configs["deployment_name"],
        deployment_configs["config_dict"],
    )
    localstore.add(
        deployment_configs["operator_name"],
        deployment_configs["deployment_name"],
        deployable_path,
    )


def describe_deployment(**configs):
    deployment_configs = build_config_dict(configs)
    operator = load_operator(deployment_configs["operator_name"])
    info_json = operator.describe(
        deployment_configs["deployment_name"], deployment_configs["config_dict"]
    )
    pprint(info_json)


def delete_deployment(**configs):
    deployment_configs = build_config_dict(configs)
    operator = load_operator(deployment_configs["operator_name"])
    operator.delete(
        deployment_configs["deployment_name"], deployment_configs["config_dict"]
    )
    localstore.prune_deployment(
        deployment_configs["operator_name"], deployment_configs["deployment_name"]
    )
