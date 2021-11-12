from .deploy import deploy


def update(bento_path, deployment_name, lambda_config):
    """
    in the case of AWS Lambda deployments, since we are using SAM cli for deploying
    the updation and deployment process is identical, hence you can just call the
    deploy functionality for updation also.
    """
    deployable_path = deploy(bento_path, deployment_name, lambda_config)

    return deployable_path
