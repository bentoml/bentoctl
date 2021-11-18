import os
import re
import shutil
import tempfile
import zipfile
from collections import namedtuple
from pathlib import Path
from urllib.request import Request, urlopen

from bentoctl.operator.constants import OFFICIAL_OPERATORS, MAIN_BRANCH
from bentoctl.utils import console


def _get_bentoctl_home():
    default_bentoctl_home = os.path.expanduser("~/bentoctl")
    bentoctl_home = Path(os.environ.get("BENTOCTL_HOME", default_bentoctl_home))
    # if not present create bentoctl and bentoctl/operators dir
    if not bentoctl_home.exists():
        os.mkdir(bentoctl_home)

    operator_home = os.path.join(bentoctl_home, "operators")
    if not os.path.exists(operator_home):
        os.mkdir(operator_home)

    deployments_home = os.path.join(bentoctl_home, "deployments")
    if not os.path.exists(deployments_home):
        os.mkdir(deployments_home)

    return bentoctl_home


BENTOCTL_HOME = os.path.expanduser(_get_bentoctl_home())

github_repo = namedtuple("github_repo", ["owner", "name", "branch"])


def _remove_if_exists(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)


def _github_archive_link(repo_owner, repo_name, repo_branch=None):
    if repo_branch in [None, ""]:
        repo_branch = MAIN_BRANCH
    return f"https://github.com/{repo_owner}/{repo_name}/archive/{repo_branch}.zip"


def _download_url(url, dest):
    # TODO: setup progress bar with rich
    file_size = None
    req = Request(url)
    u = urlopen(req)
    meta = u.info()
    if hasattr(meta, "getheaders"):
        content_length = meta.getheaders("Content-Length")
    else:
        content_length = meta.get_all("Content-Length")
    if content_length is not None and len(content_length) > 0:
        file_size = int(content_length[0])
        console.print(file_size)

    # download to a temporary file and copy it over so that if there is an existing
    # file it doesn't get corrupt.
    dst = os.path.expanduser(dest)
    f = tempfile.NamedTemporaryFile(delete=False)

    try:
        while True:
            buffer = u.read(8192)
            if len(buffer) == 0:
                break
            f.write(buffer)
        f.close()
        shutil.move(f.name, dst)
    finally:
        f.close()
        if os.path.exists(f.name):
            os.remove(f.name)


def _get_operator_dir_path(operator_name):
    # find default location
    bentoctl_home = _get_bentoctl_home()
    operator_home = os.path.join(bentoctl_home, "operators")

    # the operator's name is its directory name
    operator_dir = os.path.join(operator_home, operator_name)
    return operator_dir


def _download_repo(repo_url: str, dir_path: str) -> str:
    """
    Download the `repo_url` and put it in the home operator directory with
    the `operator_dir_name`.

    Args:
        repo_url: github archive url that points to the repo.
        dir_path: where it will be download to

    Returns:
        operator_dir: the directory to which the repo has been downloaded and saved.
    """

    # download the repo as zipfile and extract it
    with console.status(f"downloading {repo_url}"):
        _download_url(url=repo_url, dest=dir_path + ".zip")
    with zipfile.ZipFile(dir_path + ".zip", "r") as z:
        if os.path.exists(dir_path):
            _remove_if_exists(dir_path)
        extracted_repo_name = z.infolist()[0].filename
        z.extractall(operator_home)
        shutil.move(os.path.join(operator_home, extracted_repo_name), dir_path)
    _remove_if_exists(dir_path + ".zip")

    return dir_path


def _is_github_repo(link: str) -> bool:
    github_repo_re = re.compile(r"^([-_\w]+)/([-_\w]+):?([-_\w]*)$")
    return True if github_repo_re.match(link) else False


def _is_github_link(link: str) -> bool:
    github_http_re = re.compile(r"^https?://github.com/([-_\w]+)/([-_\w]+).git$")
    return True if github_http_re.match(link) else False


def _fetch_github_info(github_link):
    if not _is_github_repo(github_link) or not _is_github_link(github_link):
        raise ValueError(f"{github_link} is not a github repo")
    if _is_github_repo(github_link):
        github_repo_re = re.compile(r"^([-_\w]+)/([-_\w]+):?([-_\w]*)$")
        owner, repo, branch = github_repo_re.match(github_link).groups()
        return owner, repo, branch
    elif _is_github_link(github_link):
        github_http_re = re.compile(r"^https?://github.com/([-_\w]+)/([-_\w]+).git$")
        owner, repo = github_http_re.match(github_link).groups()
        return owner, repo, None
    else:
        raise ValueError(f"{github_link} is not a github repo")


def _is_official_operator(operator_name: str) -> bool:
    official_operators = list(OFFICIAL_OPERATORS.keys())
    return operator_name in official_operators
