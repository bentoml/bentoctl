import shutil

from bcdt.deployment_spec import DeploymentSpec
from bcdt.operator import Operator
from bcdt.operator.manager import LocalOperatorManager


def load_deployment_spec(spec_path):
    deployment_spec = DeploymentSpec.from_file(spec_path)
    operator_path = LocalOperatorManager.get(deployment_spec.operator_name).op_path
    operator = Operator(operator_path)
    operator_schema = operator.operator_schema
    operator_spec = deployment_spec.validate_operator_spec(operator_schema)

    return operator, deployment_spec, operator_spec


def deploy_spec(deployment_spec_path, keep_deployable):
    op, deployment_spec, operator_spec = load_deployment_spec(deployment_spec_path)
    deployable_path = op.deploy(
        deployment_spec.bento_path, deployment_spec.deployment_name, operator_spec
    )

    # remove the deployable
    if deployable_path is not None and keep_deployable is False:
        shutil.rmtree(deployable_path)


def update_spec(deployment_spec_path, keep_deployable):
    op, deployment_spec, operator_spec = load_deployment_spec(deployment_spec_path)
    deployable_path = op.update(
        deployment_spec.bento_path, deployment_spec.deployment_name, operator_spec
    )

    if deployable_path is not None and keep_deployable is False:
        shutil.rmtree(deployable_path)


def describe_spec(deployment_spec_path):
    op, deployment_spec, operator_spec = load_deployment_spec(deployment_spec_path)
    info_json = op.describe(deployment_spec.deployment_name, operator_spec)
    return info_json


def delete_spec(deployment_spec_path):
    op, deployment_spec, operator_spec = load_deployment_spec(deployment_spec_path)
    op.delete(deployment_spec.deployment_name, operator_spec)
    return deployment_spec.deployment_name
