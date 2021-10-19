import os
import json
import tempfile
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
        os.mkdir(os.path.join(bcdt_home, "operators"))

    return bcdt_home


def get_operator_list():
    """
    returns the operator_list from BCDT_HOME/operators/operator_list.json
    """
    bcdt_home = _get_bcdt_home()
    operator_list_path = os.path.join(bcdt_home, "operators/operator_list.json")
    try:
        with open(operator_list_path, "r") as f:
            operator_list = json.load(f)
    except FileNotFoundError:
        operator_list = {}

    return operator_list


def install_operator(path):
    """
    Adds a new name and path to operator_list
    """
    bcdt_home = _get_bcdt_home()
    operator_list_path = os.path.join(bcdt_home, "operators/operator_list.json")
    operator_list = get_operator_list()
    print("installing", path)
    with open(operator_list_path, "w") as f:
        operator = Operator(path)
        if operator.name in operator_list:
            print(f"Existing {operator.name} found! Updating...")
        operator_list[operator.name] = path
        json.dump(operator_list, f)


def _remove_if_exists(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)


def _github_archive_link(repo_owner, repo_name, repo_branch):
    return f"https://github.com/{repo_owner}/{repo_name}/archive/{repo_branch}.zip"


def _parse_github_url(github_url):
    repo_branch = MAIN_BRANCH
    if ":" in github_url:
        repo_info, repo_branch = github_url.split(":")
    else:
        repo_info = github_url
    repo_owner, repo_name = repo_info.split("/")

    return github_repo(repo_owner, repo_name, repo_branch)


def _parse_repo_info(github):
    """
    Parse the operator name that the user has given. Options to consider:
        1. Official operator - only the operator name is needed in this case
        2. Github Repo - this should be in the format 'repo_owner/repo_name:repo_branch'

    TODO:
        1. https://, git://, http://
    """
    # figure out how the user has passed the operator
    # TODO: verify with patterns.
    if github in OFFICIAL_OPERATORS.keys():
        github_url = OFFICIAL_OPERATORS[github]
        github_repo = _parse_github_url(github_url)
        operator_name = github
    else:
        github_repo = _parse_github_url(github)
        operator_name = github_repo.name

    if github_repo.branch != MAIN_BRANCH:
        operator_name += f":{github_repo.repo_branch}"

    return github_repo, operator_name


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
    dst_dir = os.path.dirname(dest)
    f = tempfile.NamedTemporaryFile(delete=False, dir=dst_dir)

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


def add_operator(github):
    github_repo, operator_name = _parse_repo_info(github)
    repo_url = _github_archive_link(
        github_repo.owner, github_repo.name, github_repo.branch
    )
    print(repo_url)

    # find default location
    bcdt_home = _get_bcdt_home()
    operator_home = os.path.join(bcdt_home, "operators")

    # the operator's name is its directory name
    operator_dir_name = operator_name
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

    install_operator(operator_dir)


def list_operators():
    operators_list = get_operator_list()
    pprint(operators_list)
