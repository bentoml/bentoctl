import json
import os
import re
import shutil
import tempfile
import typing as t
import zipfile
from collections import namedtuple
from pathlib import Path
from urllib.request import Request, urlopen

from rich.pretty import pprint
from rich.prompt import Confirm
from simple_term_menu import TerminalMenu

from bcdt.exceptions import OperatorExists, OperatorIsLocal, OperatorNotFound
from bcdt.operator import Operator
from bcdt.utils import (
    console,
    get_github_repo_details_from_archive_link,
    print_operators_list,
)


def _get_bcdt_home():
    default_bcdt_home = os.path.expanduser("~/bcdt")
    bcdt_home = Path(os.environ.get("BCDT_HOME", default_bcdt_home))
    # if not present create bcdt and bcdt/operators dir
    if not bcdt_home.exists():
        os.mkdir(bcdt_home)

    operator_home = os.path.join(bcdt_home, "operators")
    if not os.path.exists(operator_home):
        os.mkdir(operator_home)

    deployments_home = os.path.join(bcdt_home, "deployments")
    if not os.path.exists(deployments_home):
        os.mkdir(deployments_home)

    return bcdt_home


MAIN_BRANCH = "deployers"
OFFICIAL_OPERATORS = {"aws-lambda": "jjmachan/aws-lambda-deploy:deployers"}
BCDT_HOME = os.path.expanduser(_get_bcdt_home())

github_repo = namedtuple("github_repo", ["owner", "name", "branch"])
op = namedtuple("Operator", ["op_path", "op_repo_url"])


class OperatorManager:
    def __init__(self, path):
        self.path = Path(path)
        self.operator_file = self.path / "operator_list.json"
        self.ops_list = {}
        if self.operator_file.exists():
            self.ops_list = json.loads(self.operator_file.read_text())

    def list(self):
        return self.ops_list

    def get(self, op_name):
        if op_name not in self.ops_list:
            raise OperatorNotFound(operator_name=op_name)
        op_path, op_repo_url = self.ops_list[op_name]
        return op(op_path, op_repo_url)

    def _write_to_file(self):
        with open(self.operator_file, "w") as f:
            json.dump(self.ops_list, f)

    def add(self, op_name, op_path, op_repo_url=None):
        """
        Adds a new name and path to operator_list.

        Args:
            path: path to the operator codebase. Later on the operator will
            be loaded from this path.
        Returns:
            The the name of the operator installed.
        Raises:
            OperatorExists: There is another operator with the same name.
        """
        if op_name in self.ops_list:
            raise OperatorExists(operator_name=op_name)
        self.ops_list[op_name] = op(op_path, op_repo_url)
        self._write_to_file()

    def update(self, op_name, op_path, op_repo_url):
        if op_name not in self.ops_list:
            raise OperatorNotFound(operator_name=op_name)
        self.ops_list[op_name] = op(op_path, op_repo_url)
        self._write_to_file()

    def remove(self, op_name):
        if op_name not in self.ops_list:
            raise OperatorNotFound(operator_name=op_name)
        op_path, op_repo_url = self.ops_list.pop(op_name)
        self._write_to_file()

        return op_path, op_repo_url


LocalOperatorManager = OperatorManager(_get_bcdt_home() / "operators")


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


def _download_repo(repo_url: str, operator_dir_name: str) -> str:
    """
    Download the `repo_url` and put it in the home operator directory with
    the `operator_dir_name`.

    Args:
        repo_url: github archive url that points to the repo.
        operator_dir_name: the name of the directory that will be created for in
            BCDT_HOME/operators.

    Returns:
        operator_dir: the directory to which the repo has been downloaded and saved.
    """
    # find default location
    bcdt_home = _get_bcdt_home()
    operator_home = os.path.join(bcdt_home, "operators")

    # the operator's name is its directory name
    operator_dir = os.path.join(operator_home, operator_dir_name)

    # download the repo as zipfile and extract it
    with console.status(f"downloading {repo_url}"):
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
    Adds a new operator based on user_input.

    Given a user_input, we have to decide which operation the user meant by it. There
    are the option available.

        1. Interactive Mode: lists all official operators for user to choose from.

        2. Official operator: you can pass the name of one of the official operators
           and the tool with fetch it for you.

        3. Path: If you have the operator locally, either because you are building
           our own operator or if cloning and tracking the operator in some other
           remote repository (other than github) then you can just pass the path
           after the add command and it will register the local operator for you.
           This is a special case since the operator will not have an associated URL
           with it and hence cannot be updated using the tool.

        4. Github Repo: this should be in the format 'repo_owner/repo_name[:repo_branch]'.
           eg: `bcdt add bentoml/aws-lambda-repo`

        5. Git Url: of the form https://[\\w]+.git.
           eg: `bcdt add https://github.com/bentoml/aws-lambda-deploy.git`

    There user_input will be evaluated in that order

    Args:
        user_input: the input from the user after `bcdt operator add`.

    Returns:
        operator_name, if installed

    Raises:
        bcdt.exceptions.OperatorExists
    """
    # regex to match a github repo
    github_repo_re = re.compile(r"^([-_\w]+)/([-_\w]+):?([-_\w]*)$")

    if user_input == "INTERACTIVE_MODE":
        # show a simple menu with all the available official operators
        available_operators = list(OFFICIAL_OPERATORS.keys())
        tmenu = TerminalMenu(
            available_operators, title="Choose one of the Official Operators"
        )
        choice = tmenu.show()
        operator_name = available_operators[choice]

        # install the selected operator
        operator_repo = OFFICIAL_OPERATORS[operator_name]
        owner, repo, branch = github_repo_re.match(operator_repo).groups()
        repo_url = _github_archive_link(owner, repo, branch)
        operator_dir = _download_repo(repo_url=repo_url, operator_dir_name=repo)
        operator = Operator(operator_dir)
        LocalOperatorManager.add(operator.name, os.path.abspath(operator_dir), repo_url)
        return operator.name

    # Official Operator
    if user_input in OFFICIAL_OPERATORS:
        operator_repo = OFFICIAL_OPERATORS[user_input]
        owner, repo, branch = github_repo_re.match(operator_repo).groups()
        repo_url = _github_archive_link(owner, repo, branch)
        operator_dir = _download_repo(repo_url=repo_url, operator_dir_name=user_input)
        operator = Operator(operator_dir)
        LocalOperatorManager.add(operator.name, os.path.abspath(operator_dir), repo_url)
        return operator.name

    # Path
    if os.path.exists(user_input):
        try:
            operator = Operator(user_input)
        except ImportError as e:  # not a valid operator, hence ignore
            print(f"Unable to load operator in '{user_input}'")
            print(f"Error: {e}")
            return
        else:
            LocalOperatorManager.add(operator.name, os.path.abspath(user_input))
            return operator.name

    # Github Repo
    if github_repo_re.match(user_input):
        owner, repo, branch = github_repo_re.match(user_input).groups()
        repo_url = _github_archive_link(owner, repo, branch)
        operator_dir = _download_repo(repo_url, repo)
        operator = Operator(operator_dir)
        LocalOperatorManager.add(operator.name, os.path.abspath(operator_dir), repo_url)
        return operator.name

    # Git Url
    github_http_re = re.compile(r"^https?://github.com/([-_\w]+)/([-_\w]+).git$")
    if github_http_re.match(user_input):
        owner, repo = github_http_re.match(user_input).groups()
        repo_url = _github_archive_link(owner, repo)
        operator_dir = _download_repo(repo_url, repo)
        operator = Operator(operator_dir)
        LocalOperatorManager.add(operator.name, os.path.abspath(operator_dir), repo_url)
        return operator.name

    return None


def list_operators():
    operators_list = LocalOperatorManager.list()
    pprint(operators_list)


def remove_operator(name, keep_locally, skip_confirm):
    LocalOperatorManager.get(name)
    if not skip_confirm:
        proceed_with_delete = Confirm.ask(
            f"Are you sure you want to delete '{name}' operator"
        )
        if not proceed_with_delete:
            return
    op_path, op_repo_url = LocalOperatorManager.remove(name)
    if not keep_locally:
        if op_repo_url is not None:  # remove repo dir only if op was downloaded.
            shutil.rmtree(op_path)

    return name


def update_operator(name):
    if LocalOperatorManager.get(name).op_path is None:
        print("Operator is a local installation and hence cannot be updated.")
        return
    temp_dir = tempfile.mkdtemp()
    operator_path, repo_url = LocalOperatorManager.get(name)
    shutil.move(operator_path, temp_dir)
    try:
        op_path = _download_repo(repo_url, name)
        operator = Operator(op_path)
        LocalOperatorManager.update(operator.name, op_path, repo_url)
    except Exception:
        shutil.move(temp_dir, operator_path)
        raise
    shutil.rmtree(temp_dir)
