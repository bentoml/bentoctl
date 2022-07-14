import json
import logging
import os
import shutil
import typing as t
from pathlib import Path

from semantic_version import Version

from bentoctl.exceptions import (
    BentoctlException,
    OperatorExists,
    OperatorNotAdded,
    OperatorNotFound,
    OperatorNotUpdated,
)
from bentoctl.operator.constants import OFFICIAL_OPERATORS
from bentoctl.operator.operator import Operator
from bentoctl.operator.utils import (
    _get_operator_dir_path,
    _is_official_operator,
    get_semver_version,
    sort_semver_versions,
)
from bentoctl.operator.utils.github import (
    download_github_release,
    get_github_release_tags,
    get_latest_release_info,
)
from bentoctl.utils.temp_dir import TempDirectory

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

    def get(self, name: str):
        if name not in self.operators_list:
            raise OperatorNotFound(operator_name=name)
        metadata = self.operators_list[name]
        op_path = metadata["path"]
        metadata["version"] = (
            get_semver_version(metadata["version"]) if metadata.get("version") else None
        )
        return Operator(op_path, metadata)

    def get_operator_metadata(self, name):
        if name not in self.operators_list:
            raise OperatorNotFound(operator_name=name)
        operator = self.operators_list[name]
        return operator

    def _write_to_file(self):
        with open(self.operator_file, "w", encoding="UTF-8") as f:
            json.dump(self.operators_list, f)

    def _download_install_official_operator(self, repo_name: str, version: str):
        """
        Download from github releases and installs the dependencies
        Args:
            repo_name: github repo name
            version: the github tag to download. Eg('v0.2.2')
        """
        with TempDirectory(cleanup=False) as temp_dir:
            content_path = download_github_release(
                repo_name=repo_name, output_dir=temp_dir.__fspath__(), tag=version
            )
            operator = Operator(content_path)
            operator.install_dependencies()
            # copy into the operator registry
            operator_path = _get_operator_dir_path(operator.name)
            shutil.move(content_path, operator_path)
        return operator_path, operator.name

    def _install_official_operators(self, name, version=None):
        repo_name = OFFICIAL_OPERATORS[name]
        if version is None:
            latest_release = get_latest_release_info(repo_name)
            version = latest_release["tag_name"]

        operator_path, operator_name = self._download_install_official_operator(
            repo_name, version
        )
        operator_info = {
            "path": os.path.abspath(operator_path),
            "is_local": False,
            "is_official": True,
            "version": version,
        }

        return operator_name, operator_info

    def _install_custom_operators(self, name):
        is_official = False
        if not os.path.exists(name):
            raise OperatorNotAdded(
                f"Operator not Added, Unable to parse {name}. "
                "Please check docs to see the supported ways of adding operators."
            )
        is_local = True
        logger.info(f"adding operator from path ({name})")
        content_path = name
        operator = Operator(content_path)
        if operator.name in self.operators_list:
            raise OperatorExists(operator_name=operator.name)
        # install operator dependencies
        operator.install_dependencies()
        operator_info = {
            "path": os.path.abspath(Path(content_path)),
            "is_local": is_local,
            "is_official": is_official,
            "version": None,
        }
        return operator.name, operator_info

    def install_operator(self, name, version=None):
        """
        1. Official operator: you can pass the name of one of the official operators
           and the tool with fetch it for you.
        2. Path: If you have the operator locally, either because you are building
           our own operator or if cloning and tracking the operator in some other
           remote repository (other than github) then you can just pass the path
           after the install command and it will register the local operator for you.
           This is a special case since the operator will not have an associated URL
           with it and hence cannot be updated using the tool.

        Args:
            name: Name of the operator
            version: Version of the operator
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
            operator_name, operator_info = self._install_custom_operators(name)
        self.operators_list[operator_name] = operator_info
        self._write_to_file()
        return operator_name

    def update_operator(self, name: str, version: t.Optional[str] = None):
        operator = self.get(name)
        version = version if version else self.get_operator_latest_version(name)

        # make sure updation is possible
        if operator.metadata["is_local"]:
            logger.info("Local Operator need not be updated!")
            return
        if get_semver_version(operator.version) == get_semver_version(version):
            logger.info(f"Operator is already on version {version}!")
            return

        repo_name = OFFICIAL_OPERATORS[name]

        if version is None:
            raise BentoctlException(
                f"Unable to find the latest version of {name} operator"
            )
        elif isinstance(version, str):
            updated_version_str = f"v{version.strip('v')}"
        elif isinstance(version, Version):
            updated_version_str = f"v{version}"

        operator_path = _get_operator_dir_path(operator.name)
        tmp_operator_dir = TempDirectory(cleanup=False)
        tmp_operator_dir_path = tmp_operator_dir.create()
        try:
            # move the old operator to tmp location and perform updation
            shutil.move(operator_path, tmp_operator_dir_path)
            self._download_install_official_operator(repo_name, updated_version_str)
            self.operators_list[name]["version"] = updated_version_str

            return name
        except Exception as e:
            # undo all the changes
            shutil.move(
                os.path.join(tmp_operator_dir_path, operator.name), operator_path
            )
            self.operators_list[name]["version"] = f"v{operator.version}"
            raise OperatorNotUpdated(f"Error while updating operator {name} - {e}")
        finally:
            self._write_to_file()

    def remove_operator(self, name):
        if name not in self.operators_list:
            raise OperatorNotFound(operator_name=name)

        if not self.operators_list[name]["is_local"]:
            shutil.rmtree(self.operators_list[name]["path"])
        del self.operators_list[name]
        self._write_to_file()

    def get_operator_versions(self, name):
        """
        Returns the versions of the operator.
        """
        if not _is_official_operator(name):
            return []  # custom operators don't have versions
        repo_name = OFFICIAL_OPERATORS[name]
        tags = get_github_release_tags(repo_name)
        versions = [get_semver_version(tag) for tag in tags]
        return sort_semver_versions(versions)

    def get_operator_latest_version(self, name):
        versions = self.get_operator_versions(name)
        return versions[0] if versions else None

    def is_operator_on_latest_version(self, name):
        latest_version = self.get_operator_latest_version(name)
        current_version = get_semver_version(self.operators_list[name]["version"])
        return True if latest_version == current_version else False
