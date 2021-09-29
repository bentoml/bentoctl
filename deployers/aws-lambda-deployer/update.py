import argparse
import os

from utils import console
from deploy import deploy


def update(bento_bundle_path, deployment_name, config_json):
    """
    in the case of AWS Lambda deployments, since we are using SAM cli for deploying
    the updation and deployment process is identical, hence you can just call the
    deploy functionality for updation also.
    """
    deploy(bento_bundle_path, deployment_name, config_json)


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
    update(args.bento_bundle_path, args.deployment_name, args.config_json)
    console.print("[bold green]Updation Complete!")
