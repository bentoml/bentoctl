from bentoctl.operator.registry import OperatorRegistry
from bentoctl.operator.utils import _get_bentoctl_home


def get_local_operator_registry():
    return OperatorRegistry(_get_bentoctl_home() / "operators")


local_registry = get_local_operator_registry()
add = local_registry.add
list = local_registry.list  # pylint: disable=W0622
update = local_registry.update
remove = local_registry.remove
