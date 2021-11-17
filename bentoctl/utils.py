import os
import re
import typing as t

from rich import box
from rich.console import Console
from rich.table import Table

import bentoctl.operator.manager as op_manager

console = Console(highlight=False)


def get_github_repo_details_from_archive_link(repo_url: str) -> t.Tuple[str, str, str]:
    """
    Get repo_owner, repo_name, repo_branch from github archive URL of the form
    `https://github.com/jjmachan/aws-lambda-deploy/archive/deployers.zip`
    """
    github_archive_re = re.compile(
        r"https://github.com/([-_\w]+)/([-_\w]+)/archive/([-_\w]+).zip"
    )
    repo_owner, repo_name, repo_branch = github_archive_re.match(repo_url).groups()
    return (repo_owner, repo_name, repo_branch)


def print_operators_list(op_list_dict: t.Dict[str, t.Tuple[str, str]]):
    table = Table(title="", box=box.MINIMAL, padding=(0, 1, 1, 1))

    table.add_column("Operator Name")
    table.add_column("Local Operator Location", overflow="fold")
    table.add_column("Operator URL", overflow="fold")

    bcdt_home = op_manager._get_bentoctl_home()
    for op_name, (op_filepath, op_url) in op_list_dict.items():
        if op_url is None:
            op_url = "local-installation"
            op_filepath = os.path.relpath(op_filepath)
        else:
            op_filepath = "$BCDT_HOME/" + os.path.relpath(op_filepath, bcdt_home)
            owner, repo, _ = get_github_repo_details_from_archive_link(op_url)
            op_url = f"https://github.com/{owner}/{repo}"
        table.add_row(op_name, op_filepath, op_url)

    console.print(table)
