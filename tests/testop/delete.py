import argparse
import os

from .utils import get_configuration_value, console


def delete(deployment_name, lambda_config):
    print("Deleting with: ", deployment_name, lambda_config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Delete the bundle deployed on lambda",
        epilog="Check out https://github.com/bentoml/aws-lambda-deploy#readme to know more",
    )
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
    delete(args.deployment_name, lambda_config)
    console.print("[bold green]Deletion Complete!")
