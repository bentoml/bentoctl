class OperatorExists(Exception):
    """
    Raised when an existing operator was found.
    """

    pass


class OperatorNotFound(Exception):
    """
    Raised when calling an operator that is not found.
    """


class InvalidConfig(Exception):
    """
    Invalid bcdt config.
    """
