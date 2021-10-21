import os
import subprocess
import json
import base64
import shutil

import docker
import boto3
from rich.console import Console


# The Rich console to be used in the scripts for pretty printing
console = Console(highlight=False)


def is_present(project_path):
    """
    Checks for existing deployable and if found offers users 2 options
        1. overide the existing repo (usefull if there is only config changes)
        2. use the existing one for this deployment

    if no existing deployment is found, return false
    """
    if os.path.exists(project_path):
        response = console.input(
            f"Existing deployable found [[b]{project_path}[/b]]! Override? (y/n): "
        )
        if response.lower() in ["yes", "y", ""]:
            print("overiding existing deployable!")
            shutil.rmtree(project_path)
            return False
        elif response.lower() in ["no", "n"]:
            print("Using existing deployable!")
            return True
    return False


def run_shell_command(command, cwd=None, env=None, shell_mode=False):
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell_mode,
        cwd=cwd,
        env=env,
    )
    stdout, stderr = proc.communicate()
    if proc.returncode == 0:
        try:
            return json.loads(stdout.decode("utf-8")), stderr.decode("utf-8")
        except json.JSONDecodeError:
            return stdout.decode("utf-8"), stderr.decode("utf-8")
    else:
        raise Exception(
            f'Failed to run command {" ".join(command)}: {stderr.decode("utf-8")}'
        )


def get_configuration_value(config_file):
    with open(config_file, "r") as file:
        configuration = json.loads(file.read())
    return configuration


def get_ecr_login_info(region, repository_id):
    ecr_client = boto3.client("ecr", region)
    token = ecr_client.get_authorization_token(registryIds=[repository_id])
    username, password = (
        base64.b64decode(token["authorizationData"][0]["authorizationToken"])
        .decode("utf-8")
        .split(":")
    )
    registry_url = token["authorizationData"][0]["proxyEndpoint"]

    return registry_url, username, password


def create_ecr_repository_if_not_exists(region, repository_name):
    ecr_client = boto3.client("ecr", region)
    try:
        result = ecr_client.describe_repositories(repositoryNames=[repository_name])
        repository_id = result["repositories"][0]["registryId"]
        repository_uri = result["repositories"][0]["repositoryUri"]
    except ecr_client.exceptions.RepositoryNotFoundException:
        result = ecr_client.create_repository(repositoryName=repository_name)
        repository_id = result["repository"]["registryId"]
        repository_uri = result["repository"]["repositoryUri"]
    return repository_id, repository_uri


def build_docker_image(
    context_path, image_tag, dockerfile="Dockerfile", additional_build_args=None
):
    docker_client = docker.from_env()
    try:
        docker_client.images.build(
            path=context_path,
            tag=image_tag,
            dockerfile=dockerfile,
            buildargs=additional_build_args,
        )
    except (docker.errors.APIError, docker.errors.BuildError) as error:
        raise Exception(f"Failed to build docker image {image_tag}: {error}")


def push_docker_image_to_repository(
    repository, image_tag=None, username=None, password=None
):
    docker_client = docker.from_env()
    docker_push_kwags = {"repository": repository, "tag": image_tag}
    if username is not None and password is not None:
        docker_push_kwags["auth_config"] = {"username": username, "password": password}
    try:
        docker_client.images.push(**docker_push_kwags, stream=True, decode=True)
    except docker.errors.APIError as error:
        raise Exception(f"Failed to push docker image {image_tag}: {error}")


def create_s3_bucket_if_not_exists(bucket_name, region):
    import boto3
    from botocore.exceptions import ClientError

    s3_client = boto3.client("s3", region)
    try:
        s3_client.get_bucket_acl(Bucket=bucket_name)
    except ClientError as error:
        if error.response and error.response["Error"]["Code"] == "NoSuchBucket":

            # NOTE: boto3 will raise ClientError(InvalidLocationConstraint) if
            # `LocationConstraint` is set to `us-east-1` region.
            # https://github.com/boto/boto3/issues/125.
            # This issue still show up in  boto3 1.13.4(May 6th 2020)
            try:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region},
                )
            except ClientError as s3_error:
                if (
                    s3_error.response
                    and s3_error.response["Error"]["Code"]
                    == "InvalidLocationConstraint"
                ):
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    raise s3_error
        else:
            raise error


def generate_docker_image_tag(registry_uri, bento_name, bento_version):
    image_tag = f"{bento_name}-{bento_version}".lower()
    return f"{registry_uri}:{image_tag}"
