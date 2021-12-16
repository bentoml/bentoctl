import os
import re
import tempfile
from pathlib import Path

from git import Repo

from bentoctl.operator.constants import OFFICIAL_OPERATORS
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

    return bentoctl_home


def _get_operator_dir_path(operator_name):
    # find default location
    bentoctl_home = _get_bentoctl_home()
    operator_home = os.path.join(bentoctl_home, "operators")

    # the operator's name is its directory name
    operator_dir = os.path.join(operator_home, operator_name)
    return operator_dir


def _is_github_repo(link: str) -> bool:
    github_repo_re = re.compile(r"^([-_\w]+)/([-_\w]+):?([-_\w]*)$")
    return True if github_repo_re.match(link) else False


git_http_re = re.compile(r"^https://[.\w]+/([-_.\w]+)/([-_\w]+).git$")
git_ssh_re = re.compile(r"^git@[\w]+.[\w]+:([-_.\w]+)/([-_\w]+).git$")


def _is_git_link(link: str) -> bool:
    return True if git_http_re.match(link) or git_ssh_re.match(link) else False


def fetch_git_info(git_url):
    if not _is_git_link(git_url):
        raise ValueError(f"{git_url} is not a git link")

    if git_url.startswith("https://"):
        owner, repo = git_http_re.match(git_url).groups()
    elif git_url.startswith("git@"):
        owner, repo = git_ssh_re.match(git_url).groups()
    else:
        raise ValueError(f"{git_url} is not a git link")

    return owner, repo


def _fetch_github_info(github_link):
    if not _is_github_repo(github_link):
        raise ValueError(f"{github_link} is not a github repo")
    github_repo_re = re.compile(r"^([-_\w]+)/([-_\w]+):?([-_\w]*)$")
    owner, repo, branch = github_repo_re.match(github_link).groups()
    branch = branch if branch != "" else None

    return owner, repo, branch


def _is_official_operator(operator_name: str) -> bool:
    official_operators = list(OFFICIAL_OPERATORS.keys())
    return operator_name in official_operators


def _clone_git_repo(git_url, branch=None):
    """
    Clone git repo into a temp directory. If branch is provided it checks out to it.
    This assumes that git is installed in the system and that you the proper keys.
    """
    with console.status(f"Cloning {git_url}"):
        temp_operator_repo = tempfile.mkdtemp()
        repo = Repo.clone_from(git_url, temp_operator_repo)
        if branch is not None:
            # checkout to the branch
            repo.git.checkout(branch)

    return temp_operator_repo
