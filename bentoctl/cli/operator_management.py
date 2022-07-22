import os

import click
from rich.prompt import Confirm
from rich.table import Table

from bentoctl.cli.utils import BentoctlCommandGroup
from bentoctl.console import console
from bentoctl.exceptions import BentoctlException
from bentoctl.operator import get_local_operator_registry
from bentoctl.operator.constants import OFFICIAL_OPERATORS
from bentoctl.utils import is_debug_mode

local_operator_registry = get_local_operator_registry()


def get_operator_management_subcommands():
    @click.group(name="operator", cls=BentoctlCommandGroup)
    def operator_management():
        """
        Sub-commands to install, list, uninstall and update operators.

        To see the list of all the operators available and their comparisons check out
        <link to comparisons>.
        """

    @operator_management.command(name="list")
    def list_operator_command():  # pylint: disable=unused-variable
        """
        List all the available operators.

        Lists the operator, the path from where you can access operator locally and
        if the operator was pulled from github, the github URL is also shown.
        """
        operators_list = local_operator_registry.list()
        print_operator_list(operators_list)

    @operator_management.command()
    @click.argument("name", required=False)
    @click.option("--version", "-v", type=click.STRING)
    def install(name=None, version=None):  # pylint: disable=unused-variable
        """
        install operators.

        There are 3 ways to install an operator into bentoctl and they are -

        1. Interactive Mode: lists all official operators for user to choose from. Just
           type `bentoctl operator install` to enter this mode.

        2. Official operator: you can pass the name of one of the official operators
           and the tool with fetch it for you.
           eg. `bentoctl operator install aws-lambda`

           Available operators: [aws-lambda, aws-sagemaker, aws-ec2, azure-functions,
           azure-container-instances, google-compute-engine, google-cloud-run,
           heroku]


        3. Path: If you have the operator locally, either because you are building
           our own operator or if cloning the operator from some other
           remote repository then you can just pass the path
           after the install command and it will register the local operator for you.
           This is a special case since the operator will not have an associated URL
           with it and hence cannot be updated using the tool.

        """
        if not name:
            try:
                from simple_term_menu import TerminalMenu

                # show a simple menu with all the available official operators
                available_operators = list(OFFICIAL_OPERATORS.keys())
                tmenu = TerminalMenu(
                    available_operators, title="Choose one of the Official Operators"
                )
                choice = tmenu.show()
                name = available_operators[choice]
                # When user uses the interactive mode, we will default to the latest
                # version
                version = None
            except ImportError:
                raise BentoctlException(
                    "Please specify the name of the operator to install."
                )
        try:
            operator_name = local_operator_registry.install_operator(name, version)
            if operator_name is not None:
                click.echo(f"Installed {operator_name}!")
            else:
                click.echo(
                    f"Unable to install operator. `{name}` did not match any of the "
                    "operator installation options. Check `bentoctl operator install "
                    "--help` for mode details on how you can call this command."
                )
        except BentoctlException as e:
            e.show()

    @operator_management.command()
    @click.option(
        "-y",
        "skip_confirm",
        is_flag=True,
        help="skip the prompt asking if you are sure.",
    )
    @click.argument("name", type=click.STRING)
    def remove(name, skip_confirm):  # pylint: disable=unused-variable
        """
        [Deprecated] remove the given operator.

        This will remove the operator from the list. If the operator was
        installed locally this will not clear the codebase.
        """
        console.print(
            "[red]This command will be removed soon"
            "Use the 'operator uninstall' command.[/]"
        )
        uninstall_operator(name=name, skip_confirm=skip_confirm)

    @operator_management.command()
    @click.option(
        "-y",
        "skip_confirm",
        is_flag=True,
        help="skip the prompt asking if you are sure.",
    )
    @click.argument("name", type=click.STRING)
    def uninstall(name, skip_confirm):  # pylint: disable=unused-variable
        """
        Uninstall the given operator.

        This will remove the operator from the list. If the operator was
        installed locally this will not clear the codebase.
        """
        uninstall_operator(name=name, skip_confirm=skip_confirm)

    def uninstall_operator(name: str, skip_confirm: bool) -> None:
        if not skip_confirm:
            proceed_with_delete = Confirm.ask(
                f"Are you sure you want to delete '{name}' operator"
            )
            if not proceed_with_delete:
                return
        try:
            local_operator_registry.remove_operator(name)
            click.echo(f"operator '{name}' removed!")
        except BentoctlException as e:
            e.show()

    @operator_management.command()
    @click.argument("name")
    @click.option("--version", "-v", type=click.STRING)
    def update(name, version):  # pylint: disable=unused-variable
        """
        Update the given operator to the latest version.

        This only works for operators that have a URL associated with them. When passed
        the name of an available operator it goes and fetches the latest code from
        the Github repo and update the local codebase with it.
        """
        try:
            if local_operator_registry.is_operator_on_latest_version(name):
                click.echo(f"Operator '{name}' is already on the latest version.")
            else:
                local_operator_registry.update_operator(name, version)
                click.echo(f"Operator '{name}' updated!")
        except BentoctlException as e:
            e.show()

    return operator_management


def print_operator_list(operator_list):
    if is_debug_mode():
        console.print(operator_list)
    table = Table("Name", "Version", "Location", box=None)

    for name, info in operator_list.items():
        if info.get("is_official", False):
            table.add_row(name, info["version"], info["path"])
        elif info.get("is_local", False):
            location_str = os.path.join(
                "$HOME", os.path.relpath(info["path"], os.path.expanduser("~"))
            )
            table.add_row(name, "", location_str)
    console.print(table)
