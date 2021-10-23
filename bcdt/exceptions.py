class BCDTBaseException(Exception):
    """
    Base class for all of bcdt's exceptions.
    Each custom exception is derived from this base class.
    """


class OperatorExists(BCDTBaseException):
    """
    Raised when an existing operator was found.
    """

    pass


class OperatorNotFound(BCDTBaseException):
    """
    Raised when calling an operator that is not found.
    """


class InvalidConfig(BCDTBaseException):
    """
    Invalid bcdt config.
    """
