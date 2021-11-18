from bentoctl.operator.registry import OperatorRegistry
from bentoctl.operator.utils import _get_bentoctl_home


def get_local_operator_registry():
    return OperatorRegistry(_get_bentoctl_home() / "operators")
