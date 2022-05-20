import os

from bentoctl.exceptions import BentoctlException

BENTOML_DOCKER_FILE_PATH = "./env/docker/Dockerfile"


def create_deployable_from_local_bentostore(
    bento_path: str,
    destination_dir: str,  # pylint: disable=unused-argument
    bento_metadata: dict,  # pylint: disable=unused-argument
    overwrite_deployable=None,  # pylint: disable=unused-argument
):
    """
    The deployable is the bento along with all the modifications (if any)
    requried to deploy to the cloud service.

    Parameters
    ----------
    bento_path: str
        Path to the bento from the bento store.
    destination_dir: str
        directory to create the deployable into.
    bento_metadata: dict
        metadata about the bento.

    Returns
    -------
    dockerfile_path : str
        path to the dockerfile.
    docker_context_path : str
        path to the docker context.
    additional_build_args : dict
        Any addition build arguments that need to be passed to the
        docker build command
    """
    docker_file_path = os.path.join(bento_path, BENTOML_DOCKER_FILE_PATH)
    if not os.path.exists(docker_file_path):
        raise BentoctlException(
            "Could not locate Dockerfile in the bento_path provided."
            f"dockerfile: {docker_file_path}, bento_path: {bento_path}"
        )

    additional_build_args = None
    return docker_file_path, bento_path, additional_build_args
