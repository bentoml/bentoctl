import json
import logging
import os
import re
import shutil
import typing as t
from pathlib import Path

from bentoctl.exceptions import (
    OperatorConfigNotFound,
    OperatorExists,
    OperatorIsLocal,
    OperatorNotFound,
)
from bentoctl.operator.constants import OFFICIAL_OPERATORS
from bentoctl.operator.operator import Operator
from bentoctl.operator.utils import (
    _get_operator_dir_path,
    _is_github_repo,
    clone_operator_repo,
    _is_official_operator,
    _is_git_link,
)

logger = logging.getLogger(__name__)


class OperatorRegistry:
    def __init__(self, path):
        self.path = Path(path)
        self.operator_file = self.path / "operator_list.json"
        self.operators_list = {}
        if os.path.exists(self.operator_file):
            with open(self.operator_file, encoding="utf-8") as f:
                self.operators_list = json.load(f)

    def list(self):
        return self.operators_list

    def get(self, name):
        if name not in self.operators_list:
            raise OperatorNotFound(operator_name=name)
        op = self.operators_list[name]
        op_path = op["path"]
        git_url = op["git_url"]
        return Operator(op_path, git_url)

    def _write_to_file(self):
        with open(self.operator_file, "w", encoding="UTF-8") as f:
            json.dump(self.operators_list, f)

    def _add_to_registry(self, operator):
        if operator.name in self.operators_list:
            raise OperatorExists(operator.name)

        self.operators_list[operator.name] = {
            "path": os.path.abspath(operator.path),
            "git_url": operator.git_url,
            "git_branch": operator.git_branch,
        }
        self._write_to_file()
        return operator.name

    def add(self, user_input):
        if _is_official_operator(user_input):
            logger.info("adding official operator")
            return self.add_official_operator(user_input)

        elif os.path.exists(user_input):
            logger.info(f"adding operator from path ({user_input})")
            return self.add_from_path(user_input)

        elif _is_github_repo(user_input):
            logger.info("Adding from github repo")
            return self.add_from_github(user_input)

        elif _is_git_link(user_input):
            logger.info("Adding from git repo")
            return self.add_from_git(user_input)

    def add_from_path(self, operator_path: t.Union[Path, str]) -> str:
        return self._add_to_registry(Operator(operator_path))

    def add_from_github(self, github_repo):
        """
        2. Github Repo: this should be in the format
           `repo_owner/repo_name[:repo_branch]`.
           eg: `bentoctl add bentoml/aws-lambda-repo`

        """
        if not _is_github_repo(github_repo):
            raise ValueError(f"{github_repo} is not a Github repo.")
        github_repo_re = re.compile(r"^([-_\w]+)/([-_\w]+):?([-_\w]*)$")
        owner, repo, branch = github_repo_re.match(github_repo).groups()
        branch = None if branch == "" else branch
        github_git_link = f"https://github.com/{owner}/{repo}.git"

        return self.add_from_git(github_git_link, branch)

    def add_from_git(self, git_url, branch=None):
        """
        Adds a git url. This method with clone the operator repo and add it into
        the registry.

        Args:
            git_url: of the form https://[\\w]+.git.
            branch (Optional): checkout to this branch.
        """
        tmp_repo_path = clone_operator_repo(git_url, branch)
        try:
            operator = Operator(tmp_repo_path, git_url, branch)
        except OperatorConfigNotFound:
            raise OperatorConfigNotFound(
                msg="`operator_config.py` not found in the operator."
            )

        operator_path = _get_operator_dir_path(operator.name)
        shutil.move(tmp_repo_path, operator_path)
        operator.path = Path(operator_path)
        return self._add_to_registry(operator)

    def add_official_operator(self, name):
        """
        1. Official operator: you can pass the name of one of the official operators
           and the tool with fetch it for you.
        """
        if name not in OFFICIAL_OPERATORS:
            raise ValueError(f"{name} is not an Official Operator of bentoctl.")
        return self.add_from_github(OFFICIAL_OPERATORS[name])

    def update(self, name):
        operator = self.get(name)
        if operator.git_url is None:
            raise OperatorIsLocal
        temp_operator_repo = clone_operator_repo(operator.git_url, operator.git_branch)

        shutil.rmtree(operator.path)
        shutil.move(temp_operator_repo, operator.path)

    def remove(self, name, delete_from_disk=False):
        if name not in self.operators_list:
            raise OperatorNotFound(operator_name=name)
        operator_path = self.operators_list[name]["path"]
        del self.operators_list[name]
        self._write_to_file()

        if delete_from_disk:
            shutil.rmtree(operator_path)
