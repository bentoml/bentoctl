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


def deploy_bundle(bento_bundle, **metadata):
    metadata, spec = build_config_dict(metadata)
    operator = load_operator(metadata["operator_name"])
    deployable_path = operator.deploy(
        bento_bundle,
        metadata["deployment_name"],
        spec,
    )

    # the bcdt config for deployable
    bcdt_config = {
        "appVersion": "v1",
        "metadata": metadata,
        "spec": spec,
    }

    # add to localstore
    localstore.add(
        metadata["operator_name"],
        metadata["deployment_name"],
        deployable_path,
        bcdt_config,
    )


def update_deployment(bento_bundle, **metadata):
    metadata, spec = build_config_dict(metadata)
    operator = load_operator(metadata["operator_name"])
    deployable_path = operator.update(
        bento_bundle,
        metadata["deployment_name"],
        spec,
    )

    # the bcdt config for deployable
    bcdt_config = {
        "appVersion": "v1",
        "metadata": metadata,
        "spec": spec,
    }

    # add to localstore
    localstore.add(
        metadata["operator_name"],
        metadata["deployment_name"],
        deployable_path,
        bcdt_config,
    )


def describe_deployment(**metadata):
    metadata, spec = build_config_dict(metadata)
    operator = load_operator(metadata["operator_name"])
    info_json = operator.describe(metadata["deployment_name"], spec)
    pprint(info_json)


def delete_deployment(**metadata):
    metadata, spec = build_config_dict(metadata)
    operator = load_operator(metadata["operator_name"])
    operator.delete(metadata["deployment_name"], spec)
    localstore.prune_deployment(metadata["operator_name"], metadata["deployment_name"])
