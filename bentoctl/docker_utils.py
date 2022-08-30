from collections import OrderedDict

import docker
from bentoml._internal.utils import buildx
from rich.live import Live

from bentoctl.console import console
from bentoctl.deployment_config import DeploymentConfig
from bentoctl.exceptions import BentoctlDockerException
from bentoctl.utils.temp_dir import TempDirectory

# default location were dockerfile can be found
DOCKERFILE_PATH = "env/docker/Dockerfile"


class DockerPushProgressBar:
    layers = OrderedDict()

    def sizeof_fmt(self, num, suffix="B"):
        if num is None:
            return None
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f}Yi{suffix}"

    def format_progress_detail(self, progress_detail):
        current = self.sizeof_fmt(progress_detail.get("current"))
        total = self.sizeof_fmt(progress_detail.get("total"))

        if current is None or total is None:
            return ""
        else:
            return f"{current}/{total}"

    def update(self, line):
        status = line.get("status")
        layer_id = line.get("id")
        progress_str = self.format_progress_detail(line.get("progressDetail"))
        self.layers[layer_id] = {"status": status, "progress_str": progress_str}

    def __rich_console__(self, *_):
        progress_table = []
        for layer_id, line in self.layers.items():
            progress_table.append(
                f"{layer_id}: {line.get('status')} {line.get('progress_str')}"
            )

        yield "\n".join(progress_table)


def generate_deployable_container(
    tag: str, deployment_config: DeploymentConfig, cleanup: bool
):
    with TempDirectory(cleanup=cleanup) as dist_dir:
        if cleanup is False:
            # --debug flag is passed. show the path for the saved deployable
            console.print(
                f"In debug mode. Intermediate bento saved to [b]{dist_dir}[/b]"
            )
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
            "load": True,  # loading built container to local registry.
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


def tag_docker_image(image_name, image_tag):
    docker_client = docker.from_env()
    try:
        img = docker_client.images.get(image_name)
        was_tagged = img.tag(image_tag)
        if not was_tagged:
            raise BentoctlDockerException(
                "Failed to tag docker image! tag function returned False"
            )
    except docker.errors.ImageNotFound:
        raise BentoctlDockerException(
            f"Failed to tag Docker image, {image_name} not found."
        )
    except docker.errors.APIError as error:
        raise BentoctlDockerException(
            f"Failed to tag docker image {image_tag}: {error}"
        )


def push_docker_image_to_repository(
    repository, image_tag=None, username=None, password=None
):
    docker_client = docker.from_env()
    docker_push_kwags = {"repository": repository, "tag": image_tag}
    if username is not None and password is not None:
        docker_push_kwags["auth_config"] = {"username": username, "password": password}
    try:
        progress_bar = DockerPushProgressBar()
        with Live(progress_bar) as live:
            for line in docker_client.images.push(
                **docker_push_kwags, decode=True, stream=True
            ):
                if "id" in line:
                    progress_bar.update(line)
                    live.update(progress_bar)
                elif "status" in line:
                    print(line.get("status"))
                elif "errorDetail" in line:
                    raise BentoctlDockerException(
                        f"Failed to push docker image. {line['error']}"
                    )
        console.print(":rocket: Image pushed!")
    except docker.errors.APIError as error:
        raise BentoctlDockerException(
            f"Failed to push docker image {image_tag}: {error}"
        )
