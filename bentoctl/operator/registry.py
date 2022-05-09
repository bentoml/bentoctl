import json
import logging
import os
import shutil
import tarfile
from pathlib import Path

from bentoctl.exceptions import (
    BentoctlException,
    OperatorExists,
    OperatorNotAdded,
    OperatorNotFound,
    OperatorNotUpdated,
    OperatorRegistryException,
)
from bentoctl.operator.utils.github import download_github_release_tarfile
from bentoctl.utils.temp_dir import TempDirectory
from bentoctl.operator.constants import OFFICIAL_OPERATORS
from bentoctl.operator.operator import Operator
from bentoctl.operator.utils.git import (
    _clone_git_repo,
    _fetch_github_info,
    _is_git_link,
    _is_github_repo,
)
from bentoctl.operator.utils import (
    _get_operator_dir_path,
    _is_official_operator,
    get_semver_version,
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
        metadata = self.operators_list[name]
        op_path = metadata["path"]
        metadata["version"] = get_semver_version(metadata["version"])
        return Operator(op_path, metadata)

    def get_operator_metadata(self, name):
        if name not in self.operators_list:
            raise OperatorNotFound(operator_name=name)
        operator = self.operators_list[name]
        return operator

    def _write_to_file(self):
        with open(self.operator_file, "w", encoding="UTF-8") as f:
            json.dump(self.operators_list, f)

    def _install_official_operators(self, name, version=None):
        with TempDirectory() as temp_dir:
            repo_name = OFFICIAL_OPERATORS[name]
            downloaded_path = download_github_release_tarfile(
                repo_name=repo_name, output_dir=temp_dir, version=version
            )
            operator = Operator(downloaded_path)
            operator_path = _get_operator_dir_path(operator.name)
            tar = tarfile.open(downloaded_path)
            tar.extractall(path=operator_path)
            tar.close()

        # install operator dependencies
        operator.install_dependencies()

        return '', {}

    def _install_custom_operators(self, name, version=None):
        is_official = False
        """
        1. download operator
        2. check is operator is already installed. We can't do this, because we 
            don't have the name of the operator before we download it
        3. install operator dependencies
        4. add operator in registry
        """
        if os.path.exists(name):
            logger.info(f"adding operator from path ({name})")
            content_path = name
            git_url = None
            git_branch = None
            is_local = True
        elif _is_github_repo(name):
            operator_git_repo = name
            owner, repo, branch = _fetch_github_info(operator_git_repo)
            git_url = f"https://github.com/{owner}/{repo}.git"
            git_branch = branch
            content_path = _clone_git_repo(git_url, version=version)
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
        # install operator dependencies
        operator.install_dependencies()

        if is_local:
            operator_path = content_path
        else:
            operator_path = _get_operator_dir_path(operator.name)
            # move operator to bentoctl home
            shutil.copytree(content_path, operator_path)

        operator.path = Path(operator_path)
        operator_info = {
            "path": os.path.abspath(operator.path),
            "git_url": git_url,
            "git_branch": git_branch,
            "is_local": is_local,
            "is_official": is_official,
            "version": version,
        }
        return operator.name, operator_info

    def add_operator(self, name, version=None):
        """
        1. Official operator: you can pass the name of one of the official operators
           and the tool with fetch it for you.

        2. Github Repo: this should be in the format
           `repo_owner/repo_name[:repo_branch]`.
           eg: `bentoctl operator install bentoml/aws-lambda-repo`

        3. Git Url: of the form https://[\\w]+.git.
           eg: `bentoctl operator install https://github.com/bentoml/aws-lambda-deploy.git`

        4. Path: If you have the operator locally, either because you are building
           our own operator or if cloning and tracking the operator in some other
           remote repository (other than github) then you can just pass the path
           after the install command and it will register the local operator for you.
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
            if name in self.operators_list:
                raise OperatorExists(operator_name=name)
            operator_name, operator_info = self._install_official_operators(
                name, version
            )
        else:
            operator_name, operator_info = self._install_custom_operators(name, version)
        self.operators_list[operator_name] = operator_info
        self._write_to_file()
        return operator_name

    def update_operator(self, name, version=None):
        try:
            operator = self.get(name)
            if operator.metadata["is_local"]:
                logger.info("Local Operator need not be updated!")
                return
            if not operator.metadata["git_url"]:
                raise OperatorRegistryException(
                    "No git url or local operator path associated with this operator."
                )
            git_url = self.operators_list[name]["git_url"]
            # update_operator from git repo
            temp_operator_path = _clone_git_repo(
                git_url=operator.metadata["git_url"], version=version
            )
            # install latest dependencies
            updated_operator = Operator(temp_operator_path)
            updated_operator.install_dependencies()

            operator_path = operator.path
            shutil.rmtree(operator_path)
            shutil.copytree(
                temp_operator_path, operator_path, copy_function=shutil.copy
            )
        except BentoctlException as e:
            raise OperatorNotUpdated(f"Error while updating operator {name} - {e}")

    def remove_operator(self, name):
        if name not in self.operators_list:
            raise OperatorNotFound(operator_name=name)

        if not self.operators_list[name]["is_local"]:
            shutil.rmtree(self.operators_list[name]["path"])
        del self.operators_list[name]
        self._write_to_file()
