import json
import os
import shutil
import subprocess

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
    with open(config_file, "r", encoding='utf-8') as file:
        configuration = json.loads(file.read())
    return configuration
