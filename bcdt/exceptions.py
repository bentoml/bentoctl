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
    """
    Raised when an existing operator was found.
    """

    pass


class OperatorNotFound(BCDTBaseException):
    """
    Raised when calling an operator that is not found.
    """


class InvalidDeploymentSpec(BCDTBaseException):
    """
    Invalid bcdt config.
    """


class DeploymentSpecNotFound(BCDTBaseException):
    """
    When deployment spec is not found.
    """


class BCDTOperatorException(BCDTBaseException):
    """
    Base class for all of bcdt's operator exceptions.
    """
