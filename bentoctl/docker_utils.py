import os
import docker


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
        print("building...")
        img, logs = docker_client.images.build(
            path=context_path,
            tag=image_tag,
            dockerfile=dockerfile,
            buildargs=additional_build_args,
        )
        print(img)
    except (docker.errors.APIError, docker.errors.BuildError) as error:
        raise Exception(f"Failed to build docker image {image_tag}: {error}")


def push_docker_image_to_repository(
    repository, image_tag=None, username=None, password=None
):
    docker_client = docker.from_env()
    docker_push_kwags = {"repository": repository, "tag": image_tag}
    if username is not None and password is not None:
        docker_push_kwags["auth_config"] = {"username": username, "password": password}
    try:
        print("pushing...")
        out = docker_client.images.push(**docker_push_kwags)
        print(out)
    except docker.errors.APIError as error:
        raise Exception(f"Failed to push docker image {image_tag}: {error}")