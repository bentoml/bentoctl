import re
import json
import subprocess


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


def generate_cloud_run_names(
    deployment_name, project_id=None, bento_name=None, bento_version=None
):
    "Generate the service name and grc tag that is used for deployments"

    service_name = re.sub("[^a-z0-9-]", "-", deployment_name.lower())
    gcr_tag = re.sub(
        "[^a-z0-9-:_]./",
        "-",
        f"gcr.io/{project_id}/{bento_name}:{bento_version}".lower(),
    )

    return service_name, gcr_tag
