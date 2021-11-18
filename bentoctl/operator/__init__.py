from bentoctl.operator.registry import OperatorRegistry
from bentoctl.operator.utils import _get_bentoctl_home


def get_local_operator_registry():
    return OperatorRegistry(_get_bentoctl_home() / "operators")


local_registry = get_local_operator_registry()
add_from_path = local_registry.add_from_path
add_official_operator = local_registry.add_official_operator
add_from_github = local_registry.add_from_github
add_from_git = local_registry.add_from_git
