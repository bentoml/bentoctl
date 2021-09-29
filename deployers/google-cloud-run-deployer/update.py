import sys

from bentoml.saved_bundle import load_bento_service_metadata

from describe import describe_cloud_run
from utils import run_shell_command, get_configuration_value, generate_cloud_run_names


def update_gcloud_run(bento_bundle_path, deployment_name, config_json):
    bundle_metadata = load_bento_service_metadata(bento_bundle_path)
    cloud_run_config = get_configuration_value(config_json)

    service_name, gcr_tag = generate_cloud_run_names(
        deployment_name,
        cloud_run_config["project_id"],
        bundle_metadata.name,
        bundle_metadata.version,
    )

    img_name = gcr_tag.split("/")[-1]
    print(f"Building and Pushing {img_name}")
    run_shell_command(
        ["gcloud", "builds", "submit", bento_bundle_path, "--tag", gcr_tag]
    )

    print(f"Updating [{img_name}] to Cloud Run Service [{service_name}]")
    run_shell_command(
        [
            "gcloud",
            "run",
            "deploy",
            service_name,
            "--image",
            gcr_tag,
            "--port",
            str(cloud_run_config.get("port")),
            "--memory",
            cloud_run_config["memory"],
            "--cpu",
            str(cloud_run_config["cpu"]),
            "--min-instances",
            str(cloud_run_config["min_instances"]),
            "--max-instances",
            str(cloud_run_config["max_instances"]),
            "--allow-unauthenticated"
            if cloud_run_config["allow_unauthenticated"]
            else "--no-allow-unauthenticated",
        ]
    )

    # show endpoint URL and other info
    print("Updation Successful!")
    describe_cloud_run(deployment_name)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception(
            "Please provide bundle path, deployment name and path to Cloud Run "
            "config file (optional)"
        )
    bento_bundle_path = sys.argv[1]
    deployment_name = sys.argv[2]
    config_json = sys.argv[3] if len(sys.argv) == 4 else "cloud_run_config.json"

    update_gcloud_run(bento_bundle_path, deployment_name, config_json)
