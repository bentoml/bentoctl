import yaml


class BentoctlException(Exception):
    """
    Base class for all of bentoctl's exceptions.
    Each custom exception is derived from this base class.
    """

    def show(self):
        """
        used by CLI to generate a user readable error message.
        """
        print(f"Error [{type(self).__name__}]: ", self)


class OperatorExists(BentoctlException):
    """Raised when an existing operator was found."""

    def __init__(self, operator_name, msg=None):
        if msg is None:
            msg = f"Operator '{operator_name}' exists!"
        super(OperatorExists, self).__init__(msg)
        self.operator_name = operator_name


class OperatorNotFound(BentoctlException):
    """Raised when calling an operator that is not found."""

    def __init__(self, operator_name, msg=None):
        if msg is None:
            msg = (
                f"Operator '{operator_name}' not found! Please check if the operator"
                " is already added. Use `bentoctl operator list` to see all available "
                "operators."
            )
        super(OperatorNotFound, self).__init__(msg)
        self.operator_name = operator_name


class OperatorConfigNotFound(BentoctlException):
    """
    Raised when trying to load an operator that doesn't have a operator_config.py
    file
    """

    def __init__(self, operator_path=None, msg=None):
        if msg is None:
            msg = "`operator_config.py` not found inside repo."
        super(OperatorConfigNotFound, self).__init__(msg)
        self.operator_path = operator_path


class OperatorIsLocal(BentoctlException):
    """Raised when trying to do unsupported operations on Local operators"""


class OperatorLoadException(BentoctlException):
    """Raised when trying to import an operator without the proper structure"""


class OperatorNotUpdated(BentoctlException):
    """Raised when an error is encoundered in Update."""


class OperatorNotAdded(BentoctlException):
    """Raised when calling an operator that is not found."""


class InvalidDeploymentConfig(BentoctlException):
    """Invalid bentoctl config."""

    def __init__(self, msg=None, exc=None, config_errors=None):
        if msg is None and exc is not None:
            msg_list = ["Error while parsing Deployment Config:"]
            if hasattr(exc, "problem_mark"):
                if exc.context is not None:
                    msg_list.extend([exc.problem_mark, exc.problem, exc.context])
                else:
                    msg_list.extend([exc.problem_mark, exc.problem])
            else:
                msg_list.append("YAML decoding error.")

            msg = "\n".join([str(m) for m in msg_list])

        if msg is None and config_errors is not None:
            msg_list = ["Error while parsing Deployment Config."]
            msg_list.append(yaml.safe_dump(config_errors))
            msg = "\n".join(msg_list)

        super(InvalidDeploymentConfig, self).__init__(msg)


class DeploymentConfigNotFound(BentoctlException):
    """
    When deployment config is not found.
    """

    def __init__(self, deployment_config_path: str = "deployment_config not found."):
        self.msg = f"deployment_config not found at <{deployment_config_path}>."
        super(DeploymentConfigNotFound, self).__init__(self.msg)


class OperatorRegistryException(BentoctlException):
    """
    Exceptions inside the registry.
    """


class PipInstallException(BentoctlException):
    """
    Raised when dependency install fails.
    """

    def __init__(self, stderr: str):
        self.stderr = stderr
        self.msg = (
            "Installing dependencies via 'pip install -r requirements.txt' failed!"
        )
        super(PipInstallException, self).__init__(self.msg)


class BentoNotFound(BentoctlException):
    """
    Raised when bento is not found.
    """

    def __init__(self, bento_tag: str):
        self.msg = f"Bento with tag <{bento_tag}> not found in Bento Store."
        super(BentoNotFound, self).__init__(self.msg)


class BentoctlDockerException(BentoctlException):
    """
    Raised when docker command fails
    """


class TemplateExists(BentoctlException):
    """
    Raised when a Template file exists.
    """

    def __init__(self, template_file_path):
        self.msg = (
            f"Generating Template files failed since <{template_file_path}> "
            "already exists. Please call with --values-only to create only "
            "the values file or remove the main template file in order to "
            "create a new one."
        )
        super(TemplateExists, self).__init__(self.msg)


class TemplateTypeNotDefined(BentoctlException):
    """
    When the Template type provied in the deployment config is not supported by the
    operator.
    """

    def __init__(self, template_type: str):
        self.msg = (
            f"Template type <{template_type} not supported by the operator provided."
        )
        super(TemplateTypeNotDefined, self).__init__(self.msg)


class BentoctlGithubException(BentoctlException):
    """
    Raised when github request fails
    """
