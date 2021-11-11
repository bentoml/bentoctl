class BCDTBaseException(Exception):
    """
    Base class for all of bcdt's exceptions.
    Each custom exception is derived from this base class.
    """

    def show(self):
        """
        used by CLI to generate a user readable error message.
        """
        print(self)


class OperatorExists(BCDTBaseException):
    """Raised when an existing operator was found."""

    def __init__(self, operator_name, msg=None):
        if msg is None:
            msg = f"Operator '{operator_name}' exists!"
        super(OperatorExists, self).__init__(msg)
        self.operator_name = operator_name


class OperatorNotFound(BCDTBaseException):
    """Raised when calling an operator that is not found."""

    def __init__(self, operator_name, msg=None):
        if msg is None:
            msg = (
                f"Operator '{operator_name}' not found! Please check if the operator"
                " is already added. Use `bcdt operator list` to see all available "
                "operators."
            )
        super(OperatorNotFound, self).__init__(msg)
        self.operator_name = operator_name


class OperatorIsLocal(BCDTBaseException):
    """Raised when trying to do unsupported operations on Local operators"""


class OperatorLoadException(BCDTBaseException):
    """Raised when trying to import an operator without the proper structure"""


class InvalidDeploymentSpec(BCDTBaseException):
    """Invalid bcdt config."""


class DeploymentSpecNotFound(BCDTBaseException):
    """
    When deployment spec is not found.
    """
