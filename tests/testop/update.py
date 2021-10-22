import argparse
import os

from .utils import console, get_configuration_value
from .deploy import deploy


def update(bento_bundle_path, deployment_name, lambda_config):
    """
    in the case of AWS Lambda deployments, since we are using SAM cli for deploying
    the updation and deployment process is identical, hence you can just call the
    deploy functionality for updation also.
    """
    deployable_path = deploy(bento_bundle_path, deployment_name, lambda_config)

    return deployable_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update the bentoml bundle deployed in lambda.",
        epilog="Check out https://github.com/bentoml/aws-lambda-deploy#readme to know more",
    )
    parser.add_argument("bento_bundle_path", help="Path to bentoml bundle")
    parser.add_argument(
        "deployment_name", help="The name you want to use for your deployment"
    )
    parser.add_argument(
        "config_json",
        help="(optional) The config file for your deployment",
        default=os.path.join(os.getcwd(), "lambda_config.json"),
        nargs="?",
    )
    args = parser.parse_args()
    lambda_config = get_configuration_value(args.config_json)
    update(args.bento_bundle_path, args.deployment_name, lambda_config)
    console.print("[bold green]Updation Complete!")
