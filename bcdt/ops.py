from rich.pretty import pprint

from bcdt.cli.config_manager import build_config_dict
from bcdt.deployment_store import LocalStore
from bcdt.exceptions import OperatorNotFound
from bcdt.operator import LocalOpsManager, Operator
from bcdt.utils import load_bento


def load_operator(operator_name):
    try:
        operator_path = LocalOpsManager.get(operator_name).op_path
    except OperatorNotFound:
        print(
            f"the operator {operator_name} is not added. Please run "
            "'bcdt operator list' to get the list of all the operator available."
        )
        raise OperatorNotFound
    return Operator(operator_path)


def deploy(deployment_spec: dict):
    try:
        operator = load_operator(deployment_spec['operator'])
        operator_schema = load_operator_schema(operator)
        validate(deployment_spec, operator_schema)
        bento_path = load_bento(deployment_spec['bento'])
        operator.deploy(bento_path, deployment_spec['name'], deployment_spec['spec'])
        return
    except BCDTBaseException:
        raise BcdtException("deploy failed: %s", BCDTBaseException)


def update(bento_bundle, **metadata):
    metadata, spec = build_config_dict(metadata)
    operator = load_operator(metadata["operator_name"])
    deployable_path = operator.update(bento_bundle, metadata["deployment_name"], spec,)

    # the bcdt config for deployable
    bcdt_config = {
        "appVersion": "v1",
        "metadata": metadata,
        "spec": spec,
    }

    # add to localstore
    LocalStore.add(
        metadata["operator_name"],
        metadata["deployment_name"],
        deployable_path,
        bcdt_config,
    )


def describe(deployment_spec):
    metadata, spec = build_config_dict(metadata)
    operator = load_operator(metadata["operator_name"])
    info_json = operator.describe(metadata["deployment_name"], spec)
    pprint(info_json)


def delete(**metadata):
    metadata, spec = build_config_dict(metadata)
    operator = load_operator(metadata["operator_name"])
    operator.delete(metadata["deployment_name"], spec)
    LocalStore.prune_deployment(metadata["operator_name"], metadata["deployment_name"])
