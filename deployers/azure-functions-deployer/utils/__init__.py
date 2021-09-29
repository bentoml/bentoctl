import sys
import subprocess
import json
import docker
import os
import shutil

from rich.console import Console


# init rich console
console = Console(highlight=False)


def run_shell_command(command, cwd=None, env=None, shell_mode=False):
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell_mode,
    )
    stdout, stderr = proc.communicate()
    default_encoding = sys.getfilesystemencoding()
    if proc.returncode == 0:
        result = stdout.decode(default_encoding)
        if result.endswith("\x1b[0m"):
            # remove console color code: \x1b[0m
            # https://github.com/Azure/azure-cli/issues/9903
            result = result.replace("\x1b[0m", "")
        try:
            return json.loads(result), stderr.decode(default_encoding)
        except json.JSONDecodeError:
            return result, stderr.decode(default_encoding)
    else:
        raise Exception(
            f'Failed to run command {" ".join(command)}: {stderr.decode(default_encoding)}'
        )


def set_cors_settings(function_name, resource_group_name):
    # To allow all, use `*` and  remove all other origins in the list.
    cors_list_result, _ = run_shell_command(
        command=[
            "az",
            "functionapp",
            "cors",
            "show",
            "--name",
            function_name,
            "--resource-group",
            resource_group_name,
        ],
    )

    if cors_list_result != "":
        for origin_url in cors_list_result["allowedOrigins"]:
            run_shell_command(
                command=[
                    "az",
                    "functionapp",
                    "cors",
                    "remove",
                    "--name",
                    function_name,
                    "--resource-group",
                    resource_group_name,
                    "--allowed-origins",
                    origin_url,
                ],
            )

        run_shell_command(
            command=[
                "az",
                "functionapp",
                "cors",
                "add",
                "--name",
                function_name,
                "--resource-group",
                resource_group_name,
                "--allowed-origins",
                "*",
            ],
        )


def get_configuration_value(config_file):
    with open(config_file, "r") as file:
        configuration = json.loads(file.read())
    return configuration


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
        docker_client.images.push(**docker_push_kwags)
    except docker.errors.APIError as error:
        raise Exception(f"Failed to push docker image {image_tag}: {error}")


def is_present(project_path):
    """
    Checks for existing deployable and if found offers users 2 options
        1. overide the existing repo (usefull if there is only config changes)
        2. use the existing one for this deployment

    if no existing deployment is found, return false
    """
    if os.path.exists(project_path):
        response = console.input(
            f"Existing deployable found [[b]{os.path.relpath(project_path)}[/b]]!"
            " Override? (y/n): "
        )
        if response.lower() in ["yes", "y", ""]:
            print("overriding existing deployable!")
            shutil.rmtree(project_path)
            return False
        elif response.lower() in ["no", "n"]:
            print("Using existing deployable!")
            return True
    return False
