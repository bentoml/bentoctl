import os
import json
import tempfile
import re
import shutil
import zipfile
from collections import namedtuple
from urllib.request import urlopen, Request

from rich.pretty import pprint

from .operator_loader import Operator
from . import BCDT_HOME


MAIN_BRANCH = "deployers"
OFFICIAL_OPERATORS = {"aws-lambda": "jjmachan/aws-lambda-deploy:deployers"}

github_repo = namedtuple("github_repo", ["owner", "name", "branch"])


def _get_bcdt_home():
    bcdt_home = os.environ.get("BCDT_HOME", BCDT_HOME)
    # if not present create bcdt and bcdt/operators dir
    if not os.path.exists(bcdt_home):
        os.mkdir(bcdt_home)

    operator_home = os.path.join(bcdt_home, "operators")
    if not os.path.exists(operator_home):
        os.mkdir(operator_home)

    deployments_home = os.path.join(bcdt_home, "deployments")
    if not os.path.exists(deployments_home):
        os.mkdir(deployments_home)

    return bcdt_home


def get_operator_list():
    """
    returns the operator_list from BCDT_HOME/operators/operator_list.json
    """
    bcdt_home = _get_bcdt_home()
    operator_list_path = os.path.join(bcdt_home, "operators/operator_list.json")

    if not os.path.exists(operator_list_path):
        return {}
    else:
        with open(operator_list_path, "r") as f:
            txt = f.read()
            if txt == "":  # if file is empty
                return {}
            return json.loads(txt)


def _install_operator(path):
    """
    Adds a new name and path to operator_list
    """
    print(f"installing from {path} ...")
    bcdt_home = _get_bcdt_home()
    operator_list_path = os.path.join(bcdt_home, "operators/operator_list.json")
    operator_list = get_operator_list()
    print("installing", path)
    with open(operator_list_path, "w") as f:
        operator = Operator(path)
        if operator.name in operator_list:
            print(f"Existing {operator.name} found!")
        operator_list[operator.name] = path
        json.dump(operator_list, f)

    return operator.name


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


def _parse_github_url(github_url):
    repo_branch = MAIN_BRANCH
    if ":" in github_url:
        repo_info, repo_branch = github_url.split(":")
    else:
        repo_info = github_url
    repo_owner, repo_name = repo_info.split("/")

    return github_repo(repo_owner, repo_name, repo_branch)


def _download_url(url, dest):
    # TODO: setup progess bar with rich
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


def _download_repo(repo_url, operator_dir_name):
    print(f"downloading {repo_url}...")
    # find default location
    bcdt_home = _get_bcdt_home()
    operator_home = os.path.join(bcdt_home, "operators")

    # the operator's name is its directory name
    operator_dir = os.path.join(operator_home, operator_dir_name)

    # download the repo as zipfile and extract it
    _download_url(url=repo_url, dest=operator_dir + ".zip")
    with zipfile.ZipFile(operator_dir + ".zip", "r") as z:
        if os.path.exists(operator_dir):
            _remove_if_exists(operator_dir)
        extracted_repo_name = z.infolist()[0].filename
        z.extractall(operator_home)
        shutil.move(os.path.join(operator_home, extracted_repo_name), operator_dir)
    _remove_if_exists(operator_dir + ".zip")

    return operator_dir


def add_operator(user_input):
    """
    Given a user_input, we have to decide which operation the user meant by it. There
    are the option available.
        0. Interactive Model: lists all official operators for user to choose
        1. Official operator: only the operator name is needed in this case
        2. Path: a file path if the operator is available locally.
        3. Github Repo: this should be in the format'repo_owner/repo_name[:repo_branch]'
        4. Git Url: of the form https://[\\w]+.git

    There user_input will be evaluated in that order
    """
    # regex to match a github repo
    github_repo_re = re.compile(r"^([-_\w]+)/([-_\w]+):?([-_\w]*)$")

    if user_input == "INTERACTIVE_MODE":
        print('List of all official operators:')
        for i, operator in enumerate(OFFICIAL_OPERATORS):
            print(f"{i+1}. {operator}")

        operator_name = input('operator name to setup: ')
        if operator_name not in OFFICIAL_OPERATORS:
            print('error!')
            return

        # install the selected operator
        operator_repo = OFFICIAL_OPERATORS[operator_name]
        owner, repo, branch = github_repo_re.match(operator_repo).groups()
        repo_url = _github_archive_link(owner, repo, branch)
        operator_dir = _download_repo(repo_url=repo_url, operator_dir_name=user_input)
        operator_name = _install_operator(operator_dir)
        return operator_name

    # Official Operator
    if user_input in OFFICIAL_OPERATORS:
        operator_repo = OFFICIAL_OPERATORS[user_input]
        owner, repo, branch = github_repo_re.match(operator_repo).groups()
        repo_url = _github_archive_link(owner, repo, branch)
        operator_dir = _download_repo(repo_url=repo_url, operator_dir_name=user_input)
        operator_name = _install_operator(operator_dir)
        return operator_name

    # Path
    if os.path.exists(user_input):
        try:
            Operator(user_input)
        except ImportError:  # not a valid operator, hence ignore
            print("Incorrect")
            pass
        else:
            operator_name = _install_operator(user_input)
            return operator_name

    # Github Repo
    if github_repo_re.match(user_input):
        owner, repo, branch = github_repo_re.match(user_input).groups()
        repo_url = _github_archive_link(owner, repo, branch)
        operator_dir = _download_repo(repo_url, repo)
        operator_name = _install_operator(operator_dir)
        return operator_name

    # Git Url
    github_http_re = re.compile(r"^https?://github.com/([-_\w]+)/([-_\w]+).git$")
    if github_http_re.match(user_input):
        owner, repo = github_http_re.match(user_input).groups()
        repo_url = _github_archive_link(owner, repo)
        operator_dir = _download_repo(repo_url, repo)
        operator_name = _install_operator(operator_dir)
        return operator_name

    return None


def list_operators():
    operators_list = get_operator_list()
    pprint(operators_list)
