import json
import logging
import os
import re
import shutil
from pathlib import Path

from bentoctl.exceptions import (
    BentoctlException,
    OperatorConfigNotFound,
    OperatorExists,
    OperatorNotAdded,
    OperatorNotFound,
    OperatorNotUpdated,
)
from bentoctl.operator.constants import OFFICIAL_OPERATORS
from bentoctl.operator.operator import Operator
from bentoctl.operator.utils import (
    _get_operator_dir_path,
    _is_git_link,
    _is_github_repo,
    _is_official_operator,
    clone_git_repo,
)

logger = logging.getLogger(__name__)


class OperatorRegistry:
    def __init__(self, path):
        self.path = Path(path)
        self.operator_file = os.path.join(self.path, "operator_list.json")
        self.operators_list = {}
        if os.path.exists(self.operator_file):
            with open(self.operator_file, encoding="UTF-8") as f:
                self.operators_list = json.load(f)

    def list(self):
        return self.operators_list

    def get(self, name):
        if name not in self.operators_list:
            raise OperatorNotFound(operator_name=name)
        operator = self.operators_list[name]
        op_path = operator["path"]
        return Operator(op_path)

    def _write_to_file(self):
        with open(self.operator_file, "w", encoding="UTF-8") as f:
            json.dump(self.operators_list, f)

    def add(self, name):
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
        if _is_official_operator(name):
            logger.info("adding official operator")
            if name not in OFFICIAL_OPERATORS:
                raise ValueError(f"{name} is not an Official Operator of bentoctl.")
            return self._add_from_github(OFFICIAL_OPERATORS[name])

        elif os.path.exists(name):
            logger.info(f"adding operator from path ({name})")
            return self._add_to_registry(tmp_operator_path=name,)

        elif _is_github_repo(name):
            logger.info("Adding from Github")
            return self._add_from_github(github_repo=name)

        elif _is_git_link(name):
            logger.info("Adding from git repo")
            tmp_operator_path = clone_git_repo(name)
            return self._add_to_registry(
                tmp_operator_path=tmp_operator_path, git_url=name
            )
        else:
            raise OperatorNotAdded(
                f"Operator not Added, Unable to parse {name}. "
                "Please check docs to see the supported ways of adding operators."
            )

    def _add_from_github(self, github_repo):
        """
        Add operators that are on Github.

        Args:
        github_repo: This should be in the format `repo_owner/repo_name[:repo_branch]`.
                     eg: `bentoctl add bentoml/aws-lambda-repo`
        """
        if not _is_github_repo(github_repo):
            raise ValueError(f"{github_repo} is not a Github repo.")
        github_repo_re = re.compile(r"^([-_\w]+)/([-_\w]+):?([-_\w]*)$")
        owner, repo, branch = github_repo_re.match(github_repo).groups()
        branch = None if branch == "" else branch
        github_git_link = f"git@github.com:{owner}/{repo}.git"
        tmp_operator_path = clone_git_repo(git_url=github_git_link, branch=branch)

        return self._add_to_registry(
            tmp_operator_path=tmp_operator_path,
            git_url=github_git_link,
            git_branch=branch,
        )

    def _add_to_registry(
        self, tmp_operator_path, git_url=None, git_branch=None, is_local_operator=False,
    ):
        """
        Add operator from a path into the registry.

        Will move the operator from tmp_operator_path into $BENOTOCTL/operators and
        write the operator and it's metadata to disk.
        """
        try:
            operator = Operator(tmp_operator_path)
        except OperatorConfigNotFound:
            raise OperatorConfigNotFound

        operator_path = _get_operator_dir_path(operator.name)
        shutil.copytree(tmp_operator_path, operator_path)
        operator.path = Path(operator_path)
        if operator.name in self.operators_list:
            raise OperatorExists(operator.name)

        # if local operator, then keep the orginal path to operator dir
        path_to_local_operator = (
            os.path.abspath(tmp_operator_path) if is_local_operator else None
        )
        self.operators_list[operator.name] = {
            "path": os.path.abspath(operator.path),
            "git_url": git_url,
            "git_branch": git_branch,
            "path_to_local_operator": path_to_local_operator,
        }
        self._write_to_file()
        return operator.name

    def update(self, name):
        try:
            operator = self.get(name)
            git_url = self.operators_list[name]["git_url"]
            if git_url is None:  # local operator
                logger.info("Updating {name} from local")
                content_path = self.operators_list[name]["path_to_local_operator"]
            else:
                git_branch = self.operators_list[name]["git_branch"]
                content_path = clone_git_repo(git_url, git_branch)

            operator_path = operator.path
            shutil.rmtree(operator_path)
            shutil.copytree(content_path, operator_path)
        except BentoctlException as e:
            raise OperatorNotUpdated(f"Error while updating operator {name} - {e}")

    def remove(self, name, remove_from_disk=False):
        if name not in self.operators_list:
            raise OperatorNotFound(operator_name=name)
        operator_path = self.operators_list[name]["path"]
        del self.operators_list[name]
        self._write_to_file()

        if remove_from_disk:
            shutil.rmtree(operator_path)
