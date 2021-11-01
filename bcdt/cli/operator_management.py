import click

from bcdt.operator.manager import (
    add_operator,
    list_operators,
    remove_operator,
    update_operator,
)


def get_operator_management_subcommands():
    @click.group(name="operators")
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
        operator_name = add_operator(name)
        if operator_name is not None:
            print(f"Added {operator_name}")
        else:
            print(f"Error adding operator {name}. Please check docs.")

    @operator_management.command()
    @click.argument("name", type=click.STRING)
    def remove(name):
        """
        Remove operators.
        """
        remove_operator(name)

    @operator_management.command()
    @click.argument("name")
    def update(name):
        """
        Update an operator given its name.
        """
        update_operator(name)

    return operator_management
