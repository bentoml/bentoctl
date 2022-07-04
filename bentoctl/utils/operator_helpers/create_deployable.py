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
    Default create_deployable() for operators that don't make any special
    modifications to the bento. This takes the bento as it is and passes the
    path to the rest of the build process.

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
    docker_context_path : str
        path to the bento.
    """
    docker_file_path = os.path.join(bento_path, BENTOML_DOCKER_FILE_PATH)
    if not os.path.exists(docker_file_path):
        raise BentoctlException(
            "Could not locate Dockerfile in the bento_path provided."
            f"dockerfile: {docker_file_path}, bento_path: {bento_path}"
        )

    return bento_path
