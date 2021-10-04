import click
from bcdt.deployers import add_deployer


def get_deployer_management_subcommands():
    @click.group(name="deployers")
    def deployer_management():
        """
        Commands to manage the various deployers.
        """
        pass

    @deployer_management.command()
    def list():
        """
        List all the available deployers.
        """
        print("list all commands")

    @deployer_management.command()
    @click.argument('name', type=click.STRING)
    def add(name):
        """
        Add deployers.
        """
        add_deployer(name)

    @deployer_management.command()
    def remove():
        """
        Remove deployers.
        """
        print("removing deployer")

    return deployer_management
