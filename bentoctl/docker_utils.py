from __future__ import annotations

import subprocess

from bentoml._internal.utils import buildx

from bentoctl.console import console
from bentoctl.deployment_config import DeploymentConfig
from bentoctl.exceptions import BentoctlDockerException
from bentoctl.utils.temp_dir import TempDirectory

# default location were dockerfile can be found
DOCKERFILE_PATH = "env/docker/Dockerfile"


def generate_deployable_container(
    tag: str, deployment_config: DeploymentConfig, cleanup: bool
) -> None:
    with TempDirectory(cleanup=cleanup) as dist_dir:
        env = {"DOCKER_BUILDKIT": "1", "DOCKER_SCAN_SUGGEST": "false"}
        buildx_args = {
            "subprocess_env": env,
            "cwd": deployment_config.create_deployable(destination_dir=str(dist_dir)),
            "file": DOCKERFILE_PATH,
            "tags": tag,
            "add_host": None,
            "allow": None,
            "build_args": None,
            "build_context": None,
            "builder": None,
            "cache_from": None,
            "cache_to": None,
            "cgroup_parent": None,
            "iidfile": None,
            "labels": None,
            "load": None,
            "metadata_file": None,
            "network": None,
            "no_cache": False,
            "no_cache_filter": None,
            "output": None,
            "platform": "linux/amd64",
            "progress": "auto",
            "pull": False,
            "push": False,
            "quiet": False,
            "secrets": None,
            "shm_size": None,
            "rm": False,
            "ssh": None,
            "target": None,
            "ulimit": None,
        }

        # run health check whether buildx is install locally
        buildx.health()
        buildx.build(**buildx_args)


def generate_tag(image_name: str, image_tag: str) -> None:
    cmd = ["docker", "tag", image_name, image_tag]
    try:
        subprocess.check_output(list(map(str, cmd)))
    except subprocess.CalledProcessError as e:
        raise BentoctlDockerException(
            f"Failed to tag Docker image, {e.stderr.decode('utf-8')}"
        )


def push_to_repository(
    image_tag: str,
    disable_content_trust: bool | None = None,
) -> None:
    cmd = ["docker", "push"]
    if disable_content_trust:
        cmd.extend(["--disable-content-trust"])
    cmd.append(image_tag)

    try:
        subprocess.check_output(list(map(str, cmd)))
        console.print(f"Successfully pushed {image_tag}")
    except subprocess.CalledProcessError as e:
        raise BentoctlDockerException(
            f"Failed to push Docker image, {e.stderr.decode('utf-8')}"
        )
