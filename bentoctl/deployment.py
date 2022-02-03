from logging import exception
import shutil

from bentoctl.deployment_config import DeploymentConfig
from bentoctl.operator import get_local_operator_registry
from bentoctl.exceptions import BentoctlException

local_operator_registry = get_local_operator_registry()


def deploy_deployment(deployment_config_path):
    try:
        deployment_resource = DeploymentConfig.from_file(deployment_config_path)
        deployable_path = deployment_resource.operator.deploy(
            bento_path=deployment_resource.bento_path,
            deployment_name=deployment_resource.deployment_name,
            deployment_spec=deployment_resource.operator_spec,
        )
        # remove the deployable
        if deployable_path is not None:
            shutil.rmtree(deployable_path)
    except Exception as e:
        raise e if isinstance(e, BentoctlException) else BentoctlException(
            f"Failed to deploy deployment. {e}"
        )


def update_deployment(deployment_config_path):
    try:
        deployment_resource = DeploymentConfig.from_file(deployment_config_path)
        deployable_path = deployment_resource.operator.update(
            bento_path=deployment_resource.bento_path,
            deployment_name=deployment_resource.deployment_name,
            deployment_spec=deployment_resource.operator_spec,
        )
        if deployable_path is not None:
            shutil.rmtree(deployable_path)
    except Exception as e:
        raise e if isinstance(e, BentoctlException) else BentoctlException(
            f"Failed to update deployment. {e}"
        )


def describe_deployment(deployment_config_path):
    try:
        deployment_resource = DeploymentConfig.from_file(deployment_config_path)
        return deployment_resource.operator.describe(
            deployment_name=deployment_resource.deployment_name,
            deployment_spec=deployment_resource.operator_spec,
        )
    except Exception as e:
        raise e if isinstance(e, BentoctlException) else BentoctlException(
            f"Failed to describe deployment. {e}"
        )


def delete_deployment(deployment_config_path):
    try:
        deployment_resource = DeploymentConfig.from_file(deployment_config_path)
        deployment_resource.operator.delete(
            deployment_name=deployment_resource.deployment_name,
            deployment_spec=deployment_resource.operator_spec,
        )
        return deployment_resource.deployment_name
    except Exception as e:
        raise e if isinstance(e, BentoctlException) else BentoctlException(
            f"Failed to delete deployment. {e}"
        )
