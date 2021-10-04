import click
from .deployer_management import get_deployer_management_subcommands


@click.group()
def bcdt():
    pass


@bcdt.command()
@click.option('--name', '-n', type=click.STRING)
@click.option('--config', '-c', type=click.Path(exists=True))
@click.argument('bento_bundle')
def deploy(bento_bundle, name, config):
    """
    Deploy a bentoml bundle to cloud.
    """
    print("deploying")
    print(bento_bundle, name, config)


@bcdt.command()
def delete():
    print('deleting')


bcdt.add_command(get_deployer_management_subcommands())
