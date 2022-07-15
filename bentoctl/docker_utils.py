from __future__ import annotations

import subprocess
import os

from bentoml._internal.utils import buildx

from bentoctl.console import console
from bentoctl.deployment_config import DeploymentConfig
from bentoctl.exceptions import BentoctlDockerException
from bentoctl.utils.temp_dir import TempDirectory

# default location were dockerfile can be found
DOCKERFILE_PATH = "env/docker/Dockerfile"


def run_subprocess_cmd(cmd: list[str], env: dict[str, str] | None = None) -> None:

    subprocess_env = os.environ.copy()
    if env is not None:
        subprocess_env.update(env)

    try:
        subprocess.check_output(list(map(str, cmd)), env=env)
    except subprocess.CalledProcessError as e:
        raise BentoctlDockerException(
            f"Failed to push Docker image, {e.stderr.decode('utf-8')}"
        )


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
    run_subprocess_cmd(["docker", "tag", image_name, image_tag])


def push_to_repository(
    image_tag: str,
    disable_content_trust: bool | None = None,
    *,
    username: str | None = None,
    password: str | None = None,
) -> None:
    if username:
        assert password, "password is required when username is provided"
        login_cmd = ["docker", "login"]
        login_cmd.extend(["-u", username, "-p", password])
        run_subprocess_cmd(login_cmd)

    push_cmd = ["docker", "push"]
    if disable_content_trust:
        push_cmd.extend(["--disable-content-trust"])
    push_cmd.append(image_tag)
    run_subprocess_cmd(push_cmd)

    console.print(f"Successfully pushed {image_tag}")
