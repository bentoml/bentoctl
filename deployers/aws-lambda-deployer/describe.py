import boto3
import os
import argparse

from botocore.exceptions import ClientError
from rich.pretty import pprint

from aws_lambda import generate_lambda_resource_names
from utils import get_configuration_value


def describe(deployment_name, config_file_path):
    # get data about cf stack
    _, stack_name, repo_name = generate_lambda_resource_names(deployment_name)
    lambda_config = get_configuration_value(config_file_path)
    cf_client = boto3.client("cloudformation", lambda_config["region"])
    try:
        stack_info = cf_client.describe_stacks(StackName=stack_name)
    except ClientError:
        print(f"Unable to find {deployment_name} in your cloudformation stack.")
        return

    info_json = {}
    stack_info = stack_info.get("Stacks")[0]
    keys = [
        "StackName",
        "StackId",
        "StackStatus",
    ]
    info_json = {k: v for k, v in stack_info.items() if k in keys}
    info_json["CreationTime"] = stack_info.get("CreationTime").strftime(
        "%m/%d/%Y, %H:%M:%S"
    )
    info_json["LastUpdatedTime"] = stack_info.get("LastUpdatedTime").strftime(
        "%m/%d/%Y, %H:%M:%S"
    )

    # get Endpoints
    outputs = stack_info.get("Outputs")
    outputs = {o["OutputKey"]: o["OutputValue"] for o in outputs}
    info_json.update(outputs)

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

    info_json = describe(args.deployment_name, args.config_json)
    pprint(info_json)
