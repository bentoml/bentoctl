import os

from rich.box import SIMPLE
from rich.table import Table

from bentoctl.console import console
from bentoctl.operator.utils import fetch_git_info


def is_debug_mode():
    return bool(os.environ.get("BENTOCTL_DEBUG"))


def print_operator_list(operator_list):
    if is_debug_mode():
        console.print(operator_list)
    table = Table("Name", "Location", box=None)

    for name, info in operator_list.items():
        if info.get("git_url") is not None:
            owner, repo = fetch_git_info(info["git_url"])
            location_str = f"{owner}/{repo} ({info['git_branch']})"
            table.add_row(name, location_str)
        else:
            location_str = os.path.join(
                "$HOME", os.path.relpath(info["path"], os.path.expanduser("~"))
            )
            table.add_row(name, location_str)

    console.print(table)
