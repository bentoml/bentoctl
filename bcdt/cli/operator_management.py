import click
from bcdt.operator_manager import add_operator, list_operators, install_operator


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
    @click.argument('name', type=click.STRING)
    def add(name):
        """
        Add operators.
        """
        add_operator(name)

    @operator_management.command()
    @click.argument('operator-path', type=click.Path(exists=True))
    def install(operator_path):
        """
        Install a operator ie. add it to the operator_list.json
        """
        install_operator(operator_path)

    @operator_management.command()
    def remove():
        """
        Remove operators.
        """
        print("removing operator")

    return operator_management
