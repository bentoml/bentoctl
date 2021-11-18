import os
import logging
import json
import shutil
import tempfile
from collections import namedtuple
from pathlib import Path

from bentoctl.exceptions import OperatorNotFound, OperatorExists, BentoctlException
from bentoctl.operator import Operator
from bentoctl.operator.constants import OFFICIAL_OPERATORS
from bentoctl.operator.utils import (
    _download_git_repo,
    _is_official_operator,
    _fetch_github_info,
    _github_archive_link,
    _is_github_link,
    _is_github_repo,
    _get_operator_dir_path,
)


logger = logging.getLogger(__name__)

op = namedtuple("Operator", ["op_path", "op_repo_url"])


class OperatorRegistry:
    def __init__(self, path):
        self.path = Path(path)
        self.operator_file = os.path.join(self.path, "operator_list.json")
        self.operators_list = None
        if self.operator_file.exists():
            self.operators_list = json.loads(
                self.operator_file.read_text(encoding="utf-8")
            )

    def list(self):
        return self.operators_list

    def get(self, name):
        if name not in self.operators_list:
            raise OperatorNotFound(operator_name=name)
        op_path, repo_url = self.operators_list[name]
        return Operator(op_path, repo_url)

    def _write_to_file(self):
        with open(self.operator_file, "w", encoding="UTF-8") as f:
            json.dump(self.operators_list, f)

    def add(self, name, path, repo_url=None):
        """
        1. Official operator: you can pass the name of one of the official operators
           and the tool with fetch it for you.

        2. Github Repo: this should be in the format
           `repo_owner/repo_name[:repo_branch]`.
           eg: `bentoctl add bentoml/aws-lambda-repo`

        3. Git Url: of the form https://[\\w]+.git.
           eg: `bentoctl add https://github.com/bentoml/aws-lambda-deploy.git`

        4. Path: If you have the operator locally, either because you are building
           our own operator or if cloning and tracking the operator in some other
           remote repository (other than github) then you can just pass the path
           after the add command and it will register the local operator for you.
           This is a special case since the operator will not have an associated URL
           with it and hence cannot be updated using the tool.

        Args:
            name: Name of the operator
        Returns:
            The the name of the operator installed.
        Raises:
            OperatorExists: There is another operator with the same name.
        """
        if name in self.operators_list:
            raise OperatorExists(operator_name=name)

        if os.path.exists(name):
            operator_path = name
            repo_url = None
            logger.log(
                f"Adding an operator from local file system ({operator_path})..."
            )
        elif _is_official_operator(name) or _is_github_repo(name) or _is_github_link(name):
            if _is_official_operator(name):
                operator_repo = OFFICIAL_OPERATORS[name]
            else:
                operator_repo = name
            owner, repo, branch = _fetch_github_info(operator_repo)
            repo_url = _github_archive_link(owner, repo, branch)
            temp_dir = tempfile.mkdtemp()
            downloaded_path = _download_git_repo(repo_url, temp_dir)
            operator_path = _get_operator_dir_path(name)
            shutil.rmtree(operator_path)
            shutil.move(downloaded_path, operator_path)
        else:
            raise OperatorNotFound(name)

        self.operators_list[name] = {
            "path": os.path.abspath(operator_path),
            "repo_url": repo_url,
        }
        self._write_to_file()

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

            operator_path = _get_operator_dir_path(name)
            shutil.rmtree(operator_path)
            shutil.move(downloaded_path, operator_path)
        except BentoctlException as e:
            raise e

    def remove(self, name, remove_from_disk=False):
        if name not in self.operators_list:
            raise OperatorNotFound(operator_name=name)
        operator_path = self.operators_list[name]["path"]
        operator_repo_url = self.operators_list[name]["repo_url"]
        del self.operators_list[name]
        self._write_to_file()

        if remove_from_disk and operator_repo_url is not None:
            shutil.rmtree(operator_path)
        return
