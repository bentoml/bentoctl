import click
import cloup

from bcdt.exceptions import BCDTBaseException
from bcdt.operator.manager import (add_operator, list_operators,
                                   remove_operator, update_operator)


def get_operator_management_subcommands():
    @cloup.group(
        name="operator", aliases=["operators", "o"], show_subcommand_aliases=True
    )
    def operator_management():
        """
        Commands to manage the various operators.
        """
        pass

    @operator_management.command()
    def list():
        """
        List all the available operators.
        """
        list_operators()

    @operator_management.command()
    @click.argument("name", default="INTERACTIVE_MODE")
    def add(name):
        """
        Add operators.
        """
        try:
            operator_name = add_operator(name)
            if operator_name is not None:
                click.echo(f"Added {operator_name}!")
            else:
                print(f"Error adding operator {name}.")
        except BCDTBaseException as e:
            e.show()

    @operator_management.command()
    @click.argument("name", type=click.STRING)
    def remove(name):
        """
        Remove operators.
        """
        try:
            op_name = remove_operator(name)
            if op_name is not None:
                click.echo(f"operator '{op_name}' removed!")
        except BCDTBaseException as e:
            e.show()

    @operator_management.command()
    @click.argument("name")
    def update(name):
        """
        Update an operator given its name.
        """
        try:
            update_operator(name)
            click.echo(f"operator '{name}' updated!")
        except BCDTBaseException as e:
            e.show()

    return operator_management
