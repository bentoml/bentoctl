class BentoctlException(Exception):
    """
    Base class for all of bentoctl's exceptions.
    Each custom exception is derived from this base class.
    """

    def show(self):
        """
        used by CLI to generate a user readable error message.
        """
        print(self)


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

    def __init__(self, operator_path, msg=None):
        if msg is None:
            msg = f"`operator_config.py` not found in {operator_path}"
        super(OperatorConfigNotFound, self).__init__(msg)
        self.operator_path = operator_path


class OperatorIsLocal(BentoctlException):
    """Raised when trying to do unsupported operations on Local operators"""


class OperatorLoadException(BentoctlException):
    """Raised when trying to import an operator without the proper structure"""


class InvalidDeploymentSpec(BentoctlException):
    """Invalid bentoctl config."""

    def __init__(self, msg=None, exc=None, spec_errors=None):
        if msg is None and exc is not None:
            msg_list = ["Error while parsing Deployment Spec:"]
            if hasattr(exc, "problem_mark"):
                if exc.context is not None:
                    msg_list.extend([exc.problem_mark, exc.problem, exc.context])
                else:
                    msg_list.extend([exc.problem_mark, exc.problem])
            else:
                msg_list.append("YAML decoding error.")

            msg = "\n".join([str(m) for m in msg_list])

        if msg is None and spec_errors is not None:
            msg_list = ["Error while parsing Deployment Spec."]
            for field, errors in spec_errors.items():
                error_msg = "\n".join(errors)
                msg_list.append(f"{field}: {error_msg}")

            msg = "\n".join(msg_list)

        super(InvalidDeploymentSpec, self).__init__(msg)


class DeploymentSpecNotFound(BentoctlException):
    """
    When deployment spec is not found.
    """
