import os
from collections import OrderedDict

import docker
from rich.live import Live

from bentoctl.console import console
from bentoctl.exceptions import BentoctlDockerException


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


def build_docker_image(
    context_path,
    image_tag,
    dockerfile="env/docker/Dockerfile",
    additional_build_args=None,
):
    docker_client = docker.from_env()
    context_path = str(context_path)
    # make dockerfile relative to context_path
    dockerfile = os.path.relpath(dockerfile, context_path)
    try:
        output_stream = docker_client.images.client.api.build(
            path=context_path,
            tag=image_tag,
            dockerfile=dockerfile,
            buildargs=additional_build_args,
            decode=True,
        )
        for line in output_stream:
            print(line.get("stream", ""), end="")
            if "errorDetail" in line:  # incase error while building.
                raise BentoctlDockerException(
                    f"Failed to build docker image {image_tag}: {line['error']}"
                )
        console.print(":hammer: Image build!")
    except (docker.errors.APIError, docker.errors.BuildError) as error:
        raise BentoctlDockerException(
            f"Failed to build docker image {image_tag}: {error}"
        )


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
