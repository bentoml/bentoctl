import logging
import subprocess
from collections import OrderedDict

import docker
from rich.live import Live

from bentoctl.console import console
from bentoctl.exceptions import BentoctlDockerException

# default location were dockerfile can be found
DOCKERFILE_PATH = "env/docker/Dockerfile"

logger = logging.getLogger(__name__)


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
    context_path: str,
    image_tag: str,
    add_host=None,
    allow=None,
    build_args=None,
    build_context=None,
    builder=None,
    cache_from=None,
    cache_to=None,
    cgroup_parent=None,
    iidfile=None,
    labels=None,
    load=True,
    metadata_file=None,
    network=None,
    no_cache=False,
    no_cache_filter=None,
    output=None,
    platform=None,
    progress="auto",
    pull=False,
    push=False,
    quiet=False,
    secrets=None,
    shm_size=None,
    rm=False,
    ssh=None,
    target=None,
    ulimit=None,
):
    from bentoml._internal.utils import buildx

    env = {"DOCKER_BUILDKIT": "1", "DOCKER_SCAN_SUGGEST": "false"}

    # run health check whether buildx is install locally
    buildx.health()

    logger.info(f"Building docker image for {image_tag}...")
    try:
        buildx.build(
            subprocess_env=env,
            cwd=context_path,
            file=DOCKERFILE_PATH,
            tags=image_tag,
            add_host=add_host,
            allow=allow,
            build_args=build_args,
            build_context=build_context,
            builder=builder,
            cache_from=cache_from,
            cache_to=cache_to,
            cgroup_parent=cgroup_parent,
            iidfile=iidfile,
            labels=labels,
            load=load,
            metadata_file=metadata_file,
            network=network,
            no_cache=no_cache,
            no_cache_filter=no_cache_filter,
            output=output,
            platform=platform,
            progress=progress,
            pull=pull,
            push=push,
            quiet=quiet,
            secrets=secrets,
            shm_size=shm_size,
            rm=rm,
            ssh=ssh,
            target=target,
            ulimit=ulimit,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed building docker image: {e}")
        if platform != "linux/amd64":
            logger.debug(
                f"""If you run into the following error: "failed to solve: pull access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed". This means Docker doesn't have context of your build platform {platform}. By default BentoML will set target build platform to the current machine platform via `uname -m`. Try again by specifying to build x86_64 (amd64) platform: bentoml containerize {image_tag} --platform linux/amd64"""  # NOQA
            )
        return False
    else:
        logger.info(f'Successfully built docker image "{image_tag}"')
        return True


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
