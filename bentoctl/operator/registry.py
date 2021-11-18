import json
import logging
import os
import shutil
import re
import tempfile
import typing as t
from collections import namedtuple
from pathlib import Path

from git import Repo

from bentoctl.exceptions import BentoctlException, OperatorExists, OperatorNotFound
from bentoctl.operator.constants import OFFICIAL_OPERATORS
from bentoctl.operator.operator import Operator
from bentoctl.operator.utils import (
    _download_git_repo,
    _fetch_github_info,
    _get_operator_dir_path,
    _github_archive_link,
    _is_github_link,
    _is_github_repo,
    _is_official_operator,
)

logger = logging.getLogger(__name__)

op = namedtuple("Operator", ["op_path", "op_repo_url"])


class OperatorRegistry:
    def __init__(self, path):
        self.path = Path(path)
        self.operator_file = self.path / "operator_list.json"
        self.operators_list = {}
        if os.path.exists(self.operator_file):
            self.operators_list = json.loads(
                self.operator_file.read_text(encoding="utf-8")
            )

    def list(self):
        return self.operators_list

    def get(self, name):
        if name not in self.operators_list:
            raise OperatorNotFound(operator_name=name)
        op_path, git_url = self.operators_list[name]
        return Operator(op_path, git_url)

    def _write_to_file(self):
        with open(self.operator_file, "w", encoding="UTF-8") as f:
            json.dump(self.operators_list, f)

    def _add(self, operator):
        self.operators_list[operator.name] = {
            "path": os.path.abspath(operator.operator_path),
            "git_url": operator.git_url,
        }
        self._write_to_file()
        return operator.name

    def add_from_path(self, operator_path: t.Union[Path, str]) -> str:
        return self._add(Operator(operator_path))

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
        tempdir = tempfile.mkdtemp()
        Repo.clone_from(git_url, tempdir)
        operator = Operator(tempdir)
        operator_path = _get_operator_dir_path(operator.name)
        shutil.move(tempdir, operator_path)

        if branch:
            # checkout to the branch
            repo = Repo(operator_path)
            repo.git.checkout(branch)

        operator.path = Path(operator_path)
        operator.git_url = git_url
        return self._add(operator)

    def add_official_operator(self, name):
        """
        1. Official operator: you can pass the name of one of the official operators
           and the tool with fetch it for you.
        """
        if name not in OFFICIAL_OPERATORS:
            raise ValueError(f"{name} is not an Official Operator of bentoctl.")
        return self.add_from_github(OFFICIAL_OPERATORS[name])

    def update(self, name):
        try:
            operator = self.get(name)
            if operator.repo_url is None:
                logger.warning(
                    "Operator is a local installation and hence cannot be updated."
                )
                return
            temp_dir = tempfile.mkdtemp()
            downloaded_path = _download_git_repo(operator.repo_url, temp_dir)

            operator_path = _get_operator_dir_path(operator.name)
            shutil.rmtree(operator_path)
            shutil.move(downloaded_path, operator_path)
        except BentoctlException as e:
            raise e

    def remove(self, name, delete_from_disk=False):
        if name not in self.operators_list:
            raise OperatorNotFound(operator_name=name)
        operator_path = self.operators_list[name]["path"]
        operator_repo_url = self.operators_list[name]["repo_url"]
        del self.operators_list[name]
        self._write_to_file()

        if delete_from_disk and operator_repo_url is not None:
            shutil.rmtree(operator_path)
        return
