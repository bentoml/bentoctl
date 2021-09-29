import os
import re
import shutil

from utils import run_shell_command, is_present

from azurefunctions.azure_api_function_json_template import AZURE_API_FUNCTION_JSON


def generate_azure_function_deployable(bento_bundle_path, project_path, azure_config):
    # check if existing deployable is present
    if is_present(project_path=project_path):
        return project_path

    current_dir_path = os.path.dirname(__file__)
    shutil.copytree(bento_bundle_path, project_path)
    shutil.copy(
        os.path.join(current_dir_path, "host.json"),
        os.path.join(project_path, "host.json"),
    )
    shutil.copy(
        os.path.join(current_dir_path, "local.settings.json"),
        os.path.join(project_path, "local.settings.json"),
    )
    shutil.copy(
        os.path.join(current_dir_path, "Dockerfile"),
        os.path.join(project_path, "Dockerfile-azure"),
    )

    app_path = os.path.join(project_path, "app")
    os.mkdir(app_path)
    shutil.copy(
        os.path.join(current_dir_path, "app_init.py"),
        os.path.join(app_path, "__init__.py"),
    )
    with open(os.path.join(app_path, "function.json"), "w") as f:
        f.write(
            AZURE_API_FUNCTION_JSON.format(
                function_auth_level=azure_config["function_auth_level"]
            )
        )


def set_cors_settings(function_name, resource_group_name):
    cors_list_result = run_shell_command(
        [
            "az",
            "functionapp",
            "cors",
            "show",
            "--name",
            function_name,
            "--resource-group",
            resource_group_name,
        ]
    )
    for origin_url in cors_list_result["allowedOrigins"]:
        run_shell_command(
            [
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
            ]
        )
    run_shell_command(
        [
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
        ]
    )


def get_docker_login_info(resource_group_name, container_registry_name):
    run_shell_command(
        [
            "az",
            "acr",
            "update",
            "--name",
            container_registry_name,
            "--admin-enabled",
            "true",
        ],
    )
    docker_login_info, err = run_shell_command(
        [
            "az",
            "acr",
            "credential",
            "show",
            "--name",
            container_registry_name,
            "--resource-group",
            resource_group_name,
        ]
    )

    if err.strip() != "":
        print("Error: ", err)
    return docker_login_info["username"], docker_login_info["passwords"][0]["value"]


def generate_resource_names(deployment_name):
    # Generate resource names base on
    # https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules

    # 1-90, alphanumeric(A-Za-z0-9) underscores, parentheses, hyphens, periods
    # scope subscription
    resource_group_name = f"{deployment_name[:80]}-resource"

    # 3-24 a-z0-9, scope: global
    storage_account_name = f"{deployment_name[0:20]}-sa"
    storage_account_name = re.sub(re.compile("[^a-z0-9]"), "0", storage_account_name)

    # Azure has no documentation on the requirements for function plan name.
    function_plan_name = deployment_name

    # same as Microsoft.Web/sites
    # 2-60, alphanumeric and hyphens. scope global
    function_name = f"{deployment_name[:55]}-fn"
    function_name = re.sub(re.compile("[^a-zA-Z0-9-]"), "-", function_name)

    # 5-50, alphanumeric scope global
    container_registry_name = f"{deployment_name[:40]}-acr"
    container_registry_name = re.sub(
        re.compile("[^a-zA-Z0-9]"), "0", container_registry_name
    )

    return (
        resource_group_name,
        storage_account_name,
        function_plan_name,
        function_name,
        container_registry_name,
    )
