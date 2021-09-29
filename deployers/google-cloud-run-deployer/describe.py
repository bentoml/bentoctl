import sys

from ruamel.yaml import YAML

from utils import generate_cloud_run_names, run_shell_command


def describe_cloud_run(deployment_name,  cloud_run_config, return_json=False):
    service_name, _ = generate_cloud_run_names(deployment_name)

    if not return_json:
        stdout, stderr = run_shell_command(
            ["gcloud", "run", "services", "describe", service_name,
            "--platform", str(cloud_run_config["platform"]),
            "--region", str(cloud_run_config["region"])]
        )
        print(stdout)
    else:
        stdout, stderr = run_shell_command(
            ["gcloud", "run", "services", "describe", service_name, 
             "--platform", str(cloud_run_config["platform"]),
             "--region", str(cloud_run_config["region"]),
             "--format=export"]
        )
        yaml = YAML()
        data = yaml.load(stdout)

        return data


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Please provide deployment_name")
    deployment_name = sys.argv[1]

    describe_cloud_run(deployment_name)
