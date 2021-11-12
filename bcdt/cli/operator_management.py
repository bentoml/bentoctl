import click
import cloup

from bcdt.exceptions import BCDTBaseException
from bcdt.operator.manager import (
    add_operator,
    list_operators,
    remove_operator,
    update_operator,
)


def get_operator_management_subcommands():
    @cloup.group(name="operator", aliases=["operators"])
    def operator_management():
        """
        Sub-commands to add, list, remove and update operators.

        To see the list of all the operators available and their comparisons check out
        <link to comparisons>.
        """

    @operator_management.command(name="list")
    def list_operator_command():
        """
        List all the available operators.

        Lists the operator, the path from where you can access operator locally and
        if the operator was pulled from github, the github URL is also shown.
        """
        list_operators()

    @operator_management.command()
    @click.argument("name", default="INTERACTIVE_MODE")
    def add(name):
        """
        Add operators.

        There are 5 ways to add an operator into bcdt and they are -

        1. Interactive Mode: lists all official operators for user to choose from. Just
           type `bcdt add` to enter this mode.

        2. Official operator: you can pass the name of one of the official operators
           and the tool with fetch it for you. You can see the list of official
           operators <link to list off operators>.
           eg. `bcdt add aws-lambda`

        3. Path: If you have the operator locally, either because you are building
           our own operator or if cloning the operator from some other
           remote repository (other than github) then you can just pass the path
           after the add command and it will register the local operator for you.
           This is a special case since the operator will not have an associated URL
           with it and hence cannot be updated using the tool.

        4. Github Repo: this should be in the format
           `repo_owner/repo_name[:repo_branch]`.
           eg: `bcdt add bentoml/aws-lambda-repo`

        5. Git Url: of the form https://[\\w]+.git.
           eg: `bcdt add https://github.com/bentoml/aws-lambda-deploy.git`

        """
        try:
            operator_name = add_operator(name)
            if operator_name is not None:
                click.echo(f"Added {operator_name}!")
            else:
                click.echo(
                    f"Unable to add operator. `{name}` did not match any of the "
                    "operator addition options. Check `bcdt operator add --help`"
                    "for mode details on how you can call this command."
                )
        except BCDTBaseException as e:
            e.show()

    @operator_management.command()
    @click.option(
        "--keep-locally", is_flag=True, help="keep the operator code locally."
    )
    @click.option(
        "-y",
        "skip_confirm",
        is_flag=True,
        help="skip the prompt asking if you are sure.",
    )
    @click.argument("name", type=click.STRING)
    def remove(name, keep_locally, skip_confirm):
        """
        Remove operators.

        This will remove the operator from the list and also remove the local codebase.
        Pass the flag `--keep-locally` to keep the operator codebase in the local
        director.
        """
        try:
            op_name = remove_operator(
                name, keep_locally=keep_locally, skip_confirm=skip_confirm
            )
            if op_name is not None:
                click.echo(f"operator '{op_name}' removed!")
        except BCDTBaseException as e:
            e.show()

    @operator_management.command()
    @click.argument("name")
    def update(name):
        """
        Update an operator given its name.

        This only works for operators that have a URL associated with them. When passed
        the name of an available operator it goes and fetches the latest code from
        the Github repo and update the local codebase with it.
        """
        try:
            update_operator(name)
            click.echo(f"operator '{name}' updated!")
        except BCDTBaseException as e:
            e.show()

    return operator_management
