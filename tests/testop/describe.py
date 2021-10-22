import os
import argparse

from rich.pretty import pprint

from .utils import get_configuration_value


def describe(deployment_name, lambda_config):
    info_json = {"deployment_name": deployment_name, "lambda_config": lambda_config}

    return info_json


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Describe the bundle deployed on lambda",
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

    lambda_config = get_configuration_value(args.config_file_path)
    info_json = describe(args.deployment_name, lambda_config)
    pprint(info_json)
