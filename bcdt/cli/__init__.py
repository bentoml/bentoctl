import click
from bcdt.cli.plugin_management import get_plugin_management_subcommands
from bcdt.ops import (
    deploy_bundle,
    describe_deployment,
    delete_deployment,
    update_deployment,
)


@click.group()
def bcdt():
    pass


@bcdt.command()
@click.option(
    "--name", "-n", type=click.STRING, help="The name you want to give the deployment"
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to config file for deployment",
)
@click.option(
    "--plugin", "-d", type=click.STRING, help="The plugin of choice to deploy"
)
@click.argument("bento_bundle")
def deploy(bento_bundle, name, config, plugin):
    """
    Deploy a bentoml bundle to cloud.
    """
    deploy_bundle(bento_bundle, name, config, plugin)


@bcdt.command()
@click.option(
    "--name", "-n", type=click.STRING, help="The name you want to give the deployment"
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to config file for deployment",
)
@click.option(
    "--plugin", "-d", type=click.STRING, help="The plugin of choice to deploy"
)
def delete(name, config, plugin):
    print("deleting")
    delete_deployment(name, config, plugin)


@bcdt.command()
@click.option(
    "--name", "-n", type=click.STRING, help="The name you want to give the deployment"
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to config file for deployment",
)
@click.option(
    "--plugin", "-d", type=click.STRING, help="The plugin of choice to deploy"
)
def describe(name, config, plugin):
    describe_deployment(name, config, plugin)


@bcdt.command()
@click.option(
    "--name", "-n", type=click.STRING, help="The name you want to give the deployment"
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to config file for deployment",
)
@click.option(
    "--plugin", "-d", type=click.STRING, help="The plugin of choice to deploy"
)
@click.argument("bento_bundle", type=click.STRING)
def update(bento_bundle, name, config, plugin):
    update_deployment(bento_bundle, name, config, plugin)


bcdt.add_command(get_plugin_management_subcommands())
