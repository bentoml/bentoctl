import click
from .deployer_management import get_deployer_management_subcommands


@click.group()
def bcdt():
    pass


@bcdt.command()
def deploy():
    print("deploying")


@bcdt.command()
def delete():
    print('deleting')


bcdt.add_command(get_deployer_management_subcommands())
