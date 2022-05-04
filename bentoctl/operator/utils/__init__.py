import os
from pathlib import Path

from bentoctl.operator.constants import OFFICIAL_OPERATORS


def _get_bentoctl_home():
    default_bentoctl_home = os.path.expanduser("~/bentoctl")
    bentoctl_home = Path(os.environ.get("BENTOCTL_HOME", default_bentoctl_home))
    # if not present create bentoctl and bentoctl/operators dir
    if not bentoctl_home.exists():
        os.mkdir(bentoctl_home)

    operator_home = os.path.join(bentoctl_home, "operators")
    if not os.path.exists(operator_home):
        os.mkdir(operator_home)

    return bentoctl_home


def _get_operator_dir_path(operator_name):
    # find default location
    bentoctl_home = _get_bentoctl_home()
    operator_home = os.path.join(bentoctl_home, "operators")

    # the operator's name is its directory name
    operator_dir = os.path.join(operator_home, operator_name)
    return operator_dir


def _is_official_operator(operator_name: str) -> bool:
    official_operators = list(OFFICIAL_OPERATORS.keys())
    return operator_name in official_operators