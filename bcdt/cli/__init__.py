import click

from bcdt.cli.operator_management import get_operator_management_subcommands
from bcdt.deployment_store import list_deployments, prune
from bcdt.ops import (
    delete_deployment,
    deploy_bundle,
    describe_deployment,
    update_deployment,
)
from bcdt.utils import print_deployments_list


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
    "--operator", "-o", type=click.STRING, help="The operator of choice to deploy"
)
@click.argument("bento_bundle")
def deploy(bento_bundle, name, config, operator):
    """
    Deploy a bentoml bundle to cloud.
    """
    deploy_bundle(
        bento_bundle, deployment_name=name, config_path=config, operator_name=operator,
    )


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
    "--operator", "-o", type=click.STRING, help="The operator of choice to deploy"
)
def delete(name, config, operator):
    """
    Delete the deployments made.
    """
    delete_deployment(deployment_name=name, config_path=config, operator_name=operator)


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
    "--operator", "-o", type=click.STRING, help="The operator of choice to deploy"
)
def describe(name, config, operator):
    """
    Shows the discription any deployment made.
    """
    describe_deployment(
        deployment_name=name, config_path=config, operator_name=operator
    )


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
    "--operator", "-o", type=click.STRING, help="The operator of choice to deploy"
)
@click.argument("bento_bundle", type=click.STRING)
def update(bento_bundle, name, config, operator):
    """
    Update deployments. Can be usered interactively.
    """
    update_deployment(
        bento_bundle=bento_bundle,
        deployment_name=name,
        config_path=config,
        operator_name=operator,
    )


@bcdt.command()
def list():
    """
    List all the active deployments.
    """
    deployments = list_deployments()
    print_deployments_list(deployments)


@bcdt.command(name="prune")
@click.option("--all", "prune_all", is_flag=True)
def prune_all(prune_all):
    """
    Prune all non-active deployables in the store.
    Use '--all' to delete every deployable.
    """
    prune(keep_latest=not prune_all)


# subcommands
bcdt.add_command(get_operator_management_subcommands())
