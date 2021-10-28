import typing as t

from rich.pretty import pprint

from bcdt.deploymentspec import DeploymentSpec
from bcdt.operator import LocalOpsManager, Operator


def load_spec(spec_path):
    deployment_spec = DeploymentSpec.from_spec_file(spec_path)
    operator_path = LocalOpsManager.get(deployment_spec.operator_name).op_path
    operator = Operator(operator_path)
    operator_schema = operator.operator_schema
    operator_spec = deployment_spec.validate_spec(operator_schema)

    return operator, deployment_spec, operator_spec


def deploy_spec(deployment_spec_path):
    op, deployment_spec, operator_spec = load_spec(deployment_spec_path)
    op.deploy(
        deployment_spec.bundle_path, deployment_spec.deployment_name, operator_spec
    )


def update_spec(deployment_spec_path):
    op, deployment_spec, operator_spec = load_spec(deployment_spec_path)
    op.deploy(
        deployment_spec.bundle_path, deployment_spec.deployment_name, operator_spec
    )


def describe_spec(deployment_spec_path):
    op, deployment_spec, operator_spec = load_spec(deployment_spec_path)
    info_json = op.describe(
        deployment_spec.bundle_path, deployment_spec.deployment_name, operator_spec
    )
    return info_json


def delete_spec(deployment_spec_path):
    op, deployment_spec, operator_spec = load_spec(deployment_spec_path)
    op.delete(
        deployment_spec.bundle_path, deployment_spec.deployment_name, operator_spec
    )
