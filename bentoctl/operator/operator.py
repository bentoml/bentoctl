import importlib
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple
from bentoctl.cli.utils import get_debug_mode

from bentoctl.exceptions import (
    OperatorConfigNotFound,
    OperatorLoadException,
    PipInstallException,
)
from bentoctl.utils import console

logger = logging.getLogger(__name__)


class Operator:
    def __init__(self, path):
        self.path = Path(path)

        # load the operator config
        if not os.path.exists(os.path.join(self.path, "operator_config.py")):
            raise OperatorConfigNotFound(operator_path=self.path)

        self.operator_config = _import_module("operator_config", self.path)

    @property
    def name(self):
        return self.operator_config.OPERATOR_NAME

    @property
    def module_name(self):
        if hasattr(self.operator_config, "OPERATOR_MODULE"):
            return self.operator_config.OPERATOR_MODULE
        else:
            self.self.operator_name

    @property
    def schema(self):
        return self.operator_config.OPERATOR_SCHEMA

    @property
    def default_template(self):
        return self.operator_config.OPERATOR_DEFAULT_TEMPLATE

    @property
    def available_templates(self):
        if hasattr(self.operator_config, "OPERATOR_AVAILABLE_TEMPLATES"):
            return self.operator_config.OPERATOR_AVAILABLE_TEMPLATES
        else:
            return [self.operator_config.OPERATOR_DEFAULT_TEMPLATE]

    def generate(
        self,
        name: str,
        spec: dict,
        template_type: str,
        destination_dir: str,
        values_only: bool = True,
    ) -> List[str]:
        """
        generates the template corresponding to the template_type.

        Parameters
        ----------
        name : str
            deployment name to be used by the template. This name will be used
            to create the resource names.
        spec : dict
            The properties of the deployment (specifications) passed from the
            deployment_config's `spec` section.
        template_type: str
            The type of template that is to be generated by the operator. The
            available ones are [terraform, cloudformation]
        destination_dir: str
            The directory into which the files are generated.
        values_only: bool
            Generate only the values files.

        Returns
        -------
        generated_path : str
            The path for the generated template.
        """
        operator = self._load_operator_module()
        return operator.generate(
            name, spec, template_type, destination_dir, values_only
        )

    def create_deployable(
        self,
        bento_path: str,
        destination_dir: str,
        bento_metadata: dict,
        overwrite_deployable: bool = True,
    ) -> Tuple[str, str, dict]:
        """
        The deployable is the bento along with all the modifications (if any)
        requried to deploy to the cloud service.

        Parameters
        ----------
        bento_path: str
            Path to the bento from the bento store.
        destination_dir: str
            directory to create the deployable into.
        bento_metadata: dict
            metadata about the bento.

        Returns
        -------
        dockerfile_path : str
            path to the dockerfile.
        docker_context_path : str
            path to the docker context.
        additional_build_args : dict
            Any addition build arguments that need to be passed to the
            docker build command
        """
        operator = self._load_operator_module()
        return operator.create_deployable(
            bento_path, destination_dir, bento_metadata, overwrite_deployable
        )

    def get_registry_info(
        self, deployment_name: str, operator_spec: str
    ) -> Tuple[str, str, str]:
        """
        Get registry information from operator.

        Parameters
        ----------
        deployment_name: str
        operator_spec: str
            Operator specifications

        Returns
        -------
        repository_url: str
            The url of the repository that is created by the operator.
        username: str
            Username for docker push authentication
        password: str
            Password for docker push authentication
        """
        operator = self._load_operator_module()
        return operator.get_registry_info(deployment_name, operator_spec)

    def install_dependencies(self):
        requirement_txt_filepath = os.path.join(self.path, "requirements.txt")
        if not os.path.exists(requirement_txt_filepath):
            logger.info(
                "requirements.txt not found in Operator, skipping installation of "
                "dependencies"
            )
            return
        with console.status("Installing dependencies from requirements.txt"):
            completedprocess = subprocess.run(
                ["pip", "install", "-r", requirement_txt_filepath],
                capture_output=True,
                check=False,
            )
        if completedprocess.returncode == 0:  # success
            logger.info(completedprocess.stdout.decode("utf-8"))
        else:
            logger.error(completedprocess.stderr.decode("utf-8"))
            raise PipInstallException(stderr=completedprocess.stderr.decode("utf-8"))

    def _load_operator_module(self):
        return _import_module(self.module_name, self.path)


def _import_module(module_name, path):
    try:
        sys.path.insert(0, os.path.abspath(path))
        module = importlib.import_module(module_name)
        return module
    except (ImportError, ModuleNotFoundError) as e:
        logger.exception(e)
        raise OperatorLoadException(f"Failed to load module {module_name} - {e}.")
