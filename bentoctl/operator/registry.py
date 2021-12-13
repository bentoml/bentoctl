import json
import logging
import os
import shutil
from pathlib import Path

from bentoctl.exceptions import (
    BentoctlException,
    OperatorExists,
    OperatorNotAdded,
    OperatorNotFound,
    OperatorNotUpdated,
    OperatorRegistryException,
)
from bentoctl.operator.constants import OFFICIAL_OPERATORS
from bentoctl.operator.operator import Operator
from bentoctl.operator.utils import (
    _clone_git_repo,
    _fetch_github_info,
    _get_operator_dir_path,
    _is_git_link,
    _is_github_repo,
    _is_official_operator,
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

        if os.path.exists(name):
            logger.info(f"adding operator from path ({name})")
            content_path = name
            git_url = None
            git_branch = None

        elif _is_official_operator(name) or _is_github_repo(name):
            if _is_official_operator(name):
                operator_repo = OFFICIAL_OPERATORS[name]
            else:
                operator_repo = name
            owner, repo, branch = _fetch_github_info(operator_repo)
            git_url = f"git@github.com:{owner}/{repo}.git"
            git_branch = branch
            content_path = _clone_git_repo(git_url, branch=branch)

        elif _is_git_link(name):
            git_url = name
            content_path = _clone_git_repo(git_url)
            git_branch = None

        else:
            OperatorNotAdded(
                f"Operator not Added, Unable to parse {name}. "
                "Please check docs to see the supported ways of adding operators."
            )

        operator = Operator(content_path)

        if operator.name in self.operators_list:
            raise OperatorExists(operator_name=operator.name)
        # move operator to bentoctl home
        operator_path = _get_operator_dir_path(operator.name)
        shutil.copytree(content_path, operator_path)
        # install operator dependencies
        operator.install_dependencies()

        operator.path = Path(operator_path)
        # if local operator, then keep the orginal path to operator dir
        path_to_local_operator = os.path.abspath(content_path) if not git_url else None

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
            if git_url:
                # update from git repo
                git_branch = self.operators_list[name]["git_branch"]
                content_path = _clone_git_repo(git_url, git_branch)
            elif self.operators_list[name]["path_to_local_operator"]:
                # update from local file path
                logger.info(f"Updating {name} from local")
                content_path = self.operators_list[name]["path_to_local_operator"]
            else:
                raise OperatorRegistryException(
                    "No git url or local operator path associated with this operator."
                )

            # install latest dependencies
            updated_operator = Operator(content_path)
            updated_operator.install_dependencies()

            operator_path = operator.path
            shutil.rmtree(operator_path)
            shutil.copytree(content_path, operator_path, copy_function=shutil.copy)
        except BentoctlException as e:
            raise OperatorNotUpdated(f"Error while updating operator {name} - {e}")

    def remove(self, name):
        if name not in self.operators_list:
            raise OperatorNotFound(operator_name=name)
        operator_path = self.operators_list[name]["path"]
        del self.operators_list[name]
        self._write_to_file()

        shutil.rmtree(operator_path)
