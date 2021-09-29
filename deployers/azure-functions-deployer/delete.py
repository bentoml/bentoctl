import sys

from utils import run_shell_command

from azurefunctions import generate_resource_names


def delete(deployment_name):
    resource_group_name, _, _, _, _ = generate_resource_names(deployment_name)
    run_shell_command(["az", "group", "delete", "-y", "--name", resource_group_name])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception(
            "Please provide deployment_name"
        )
    deployment_name = sys.argv[1]

    delete(deployment_name)
