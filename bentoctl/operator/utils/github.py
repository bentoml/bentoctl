import os.path
import tarfile

import requests

from bentoctl.exceptions import BentoctlGithubException


def github_get_call(url):
    """
    Get a GitHub API call.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to make request to {url}")


def get_github_release_info(repo_name: str, tag: str):
    """
    Get the release info of a GitHub repository.
    """
    url = f"https://api.github.com/repos/{repo_name}/releases/tags/{tag}"
    try:
        return github_get_call(url)
    except Exception as e:
        raise BentoctlGithubException(
            f"Failed to get release info for {repo_name} with {tag}"
        ) from e


def get_github_releases(repo_name):
    """
    Get the releases of a GitHub repository.
    """
    url = f"https://api.github.com/repos/{repo_name}/releases"
    try:
        return github_get_call(url)
    except Exception as e:
        raise BentoctlGithubException(f"Failed to get releases for {repo_name}") from e


def get_latest_release_info(repo_name):
    """
    Get the latest release of a GitHub repository.
    """
    url = f"https://api.github.com/repos/{repo_name}/releases/latest"
    try:
        return github_get_call(url)
    except Exception as e:
        raise BentoctlGithubException(
            f"Failed to get latest release for {repo_name}"
        ) from e


def get_github_release_tags(repo_name):
    """
    Get the tags of a GitHub repository.
    """
    releases = get_github_releases(repo_name)
    tags = [release["tag_name"] for release in releases]
    return tags


def download_github_release(repo_name: str, output_dir: str, tag: str):
    """
    Download a GitHub release in tar.gz file.
    """
    if tag:
        url = f"https://api.github.com/repos/{repo_name}/releases/tags/{tag}"
    else:
        url = f"https://api.github.com/repos/{repo_name}/releases/latest"
    try:
        release_info = github_get_call(url)
        release_name = release_info["name"]
        release_tarball_name = f"{release_name}.tar.gz"
        if release_info["assets"]:
            tarball_asset = next(
                (
                    asset
                    for asset in release_info["assets"]
                    if asset["name"] == release_tarball_name
                ),
                None,
            )
            if tarball_asset is None:
                raise Exception(
                    f"Failed to find tarball for {release_name} in {repo_name}"
                )
            tarball_url = tarball_asset["browser_download_url"]
        else:
            tarball_url = release_info["tarball_url"]
        tarball_path = os.path.join(output_dir, release_tarball_name)
        with requests.get(tarball_url, stream=True) as r:
            r.raise_for_status()
            with open(tarball_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        tar = tarfile.open(tarball_path)
        tar.extractall(path=output_dir)
        tar.close()
        operator_dir = next(
            (
                i
                for i in os.listdir(output_dir)
                if os.path.isdir(os.path.join(output_dir, i))
            ),
            None,
        )
        return os.path.join(output_dir, operator_dir)
    except Exception as e:
        raise BentoctlGithubException(
            f"Failed to download release for {repo_name}"
        ) from e
