import os
import argparse
import shutil


from .utils import (
    get_configuration_value,
    console,
)


def deploy(bento_bundle_path, deployment_name, lambda_config):
    print("deploying with: ", bento_bundle_path, deployment_name, lambda_config)
    deployabe_path = os.path.abspath("./testop_deployable")
    cur_path = os.path.dirname(__file__)
    deployable_file = os.path.join(cur_path, "./aws_lambda")
    shutil.copytree(deployable_file, deployabe_path)

    return deployabe_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Deploy the bentoml bundle to lambda.",
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
    deploy(args.bento_bundle_path, args.deployment_name, lambda_config)
    console.print("[bold green]Deployment Complete!")
