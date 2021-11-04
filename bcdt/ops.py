from bcdt.deployment_spec import DeploymentSpec
from bcdt.operator import LocalOperatorManager, Operator


def load_deployment_spec(spec_path):
    deployment_spec = DeploymentSpec.from_file(spec_path)
    operator_path = LocalOperatorManager.get(deployment_spec.operator_name).op_path
    operator = Operator(operator_path)
    operator_schema = operator.operator_schema
    operator_spec = deployment_spec.validate_operator_spec(operator_schema)

    return operator, deployment_spec, operator_spec


def load_deployment_spec(spec_path):
    deployment_spec = DeploymentSpec.from_file(spec_path)
    operator_path = LocalOperatorManager.get(deployment_spec.operator_name).op_path
    operator = Operator(operator_path)
    operator_schema = operator.operator_schema
    operator_spec = deployment_spec.validate_operator_spec(operator_schema)


def deploy_spec(deployment_spec_path):
    op, deployment_spec, operator_spec = load_deployment_spec(deployment_spec_path)
    op.deploy(
        deployment_spec.bundle_path, deployment_spec.deployment_name, operator_spec
    )


def update_spec(deployment_spec_path):
    op, deployment_spec, operator_spec = load_deployment_spec(deployment_spec_path)
    op.update(
        deployment_spec.bundle_path, deployment_spec.deployment_name, operator_spec
    )


def describe_spec(deployment_spec_path):
    op, deployment_spec, operator_spec = load_deployment_spec(deployment_spec_path)
    info_json = op.describe(
        deployment_spec.bundle_path, deployment_spec.deployment_name, operator_spec
    )
    return info_json


def delete_spec(deployment_spec_path):
    op, deployment_spec, operator_spec = load_deployment_spec(deployment_spec_path)
    op.delete(
        deployment_spec.bundle_path, deployment_spec.deployment_name, operator_spec
    )
