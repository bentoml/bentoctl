import re
import tempfile

from git import Repo

from bentoctl.console import console


git_http_re = re.compile(r"^https://[.\w]+/([-_.\w]+)/([-_\w]+).git$")
git_ssh_re = re.compile(r"^git@[\w]+.[\w]+:([-_.\w]+)/([-_\w]+).git$")


def _clone_git_repo(git_url, branch=None, version=None):
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
        if version is not None:
            # checkout to the tag
            tag = f'v{version}' if version else ""
            repo.git.checkout(tag)

    return temp_operator_repo


def _fetch_github_info(github_link):
    if not _is_github_repo(github_link):
        raise ValueError(f"{github_link} is not a github repo")
    github_repo_re = re.compile(r"^([-_\w]+)/([-_\w]+):?([-_\w]*)$")
    owner, repo, branch = github_repo_re.match(github_link).groups()
    branch = branch if branch != "" else None

    return owner, repo, branch


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


def fetch_git_repo_tags(operator_repo_dir):
    repo = Repo(path=operator_repo_dir)
    remote_repo = repo.remotes[0]
    remote_repo.fetch(refspec="refs/tags/*:refs/tags/*")
    return


def get_operator_tags(operator_repo_dir):
    repo = Repo(path=operator_repo_dir)
    remote_repo = repo.remotes[0]
    remote_repo.fetch(refspec="refs/tags/*:refs/tags/*")
    return [tag.name for tag in repo.tags]


def _is_git_link(link: str) -> bool:
    return True if git_http_re.match(link) or git_ssh_re.match(link) else False


def _is_github_repo(link: str) -> bool:
    github_repo_re = re.compile(r"^([-_\w]+)/([-_\w]+):?([-_\w]*)$")
    return True if github_repo_re.match(link) else False
