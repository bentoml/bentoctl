import shutil

from bentoctl.deployment_spec import DeploymentSpec
from bentoctl.operator import get_local_operator_registry

local_operator_registry = get_local_operator_registry()


def load_deployment_spec(spec_path):
    deployment_spec = DeploymentSpec.from_file(spec_path)
    operator = local_operator_registry.get(deployment_spec.operator_name)
    operator_schema = operator.operator_schema
    operator_spec = deployment_spec.validate_operator_spec(operator_schema)

    return operator, deployment_spec, operator_spec


def deploy_spec(deployment_spec_path):
    operator, deployment_spec, operator_spec = load_deployment_spec(
        deployment_spec_path
    )
    deployable_path = operator.deploy(
        deployment_spec.bento_path, deployment_spec.deployment_name, operator_spec
    )

    # remove the deployable
    if deployable_path is not None:
        shutil.rmtree(deployable_path)


def update_spec(deployment_spec_path):
    operator, deployment_spec, operator_spec = load_deployment_spec(
        deployment_spec_path
    )
    deployable_path = operator.update(
        deployment_spec.bento_path, deployment_spec.deployment_name, operator_spec
    )

    if deployable_path is not None:
        shutil.rmtree(deployable_path)


def describe_spec(deployment_spec_path):
    operator, deployment_spec, operator_spec = load_deployment_spec(
        deployment_spec_path
    )
    info_json = operator.describe(deployment_spec.deployment_name, operator_spec)
    return info_json


def delete_spec(deployment_spec_path):
    operator, deployment_spec, operator_spec = load_deployment_spec(
        deployment_spec_path
    )
    operator.delete(deployment_spec.deployment_name, operator_spec)
    return deployment_spec.deployment_name
