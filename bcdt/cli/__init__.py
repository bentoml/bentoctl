import argparse
from pathlib import Path

import click
from rich.pretty import pprint

from bcdt.cli.interactive import deployment_spec_builder, save_deployment_spec
from bcdt.cli.operator_management import get_operator_management_subcommands
from bcdt.deploymentspec import DeploymentSpec
from bcdt.exceptions import BCDTBaseException
from bcdt.ops import delete_spec, deploy_spec, describe_spec, update_spec


@click.group()
def bcdt():
    pass


@bcdt.command()
@click.option(
    "--name", "-n", type=click.STRING, help="The name you want to give the deployment"
)
@click.option(
    "--operator", "-o", type=click.STRING, help="The operator of choice to deploy"
)
@click.option(
    "--bento_bundle",
    "-b",
    type=click.STRING,
    help="The path to bento bundle.",
)
@click.option("--describe", is_flag=True)
@click.argument("deployment_spec", type=click.Path(), required=False)
def deploy(deployment_spec, name, operator, bento_bundle, describe):
    """
    Deploy a bentoml bundle to cloud.

    1. if interactive mode. call the interactive setup manager
    2. call deploy_bento
    3. display results from deploy_bento
    """
    try:
        if deployment_spec is None:
            deployment_spec = deployment_spec_builder(bento_bundle, name, operator)
            dspec = DeploymentSpec(deployment_spec)
            deployment_spec = save_deployment_spec(dspec.deployment_spec, Path.cwd())
            print(f"spec saved to {deployment_spec}")
        deploy_spec(deployment_spec)
        print("Successful deployment!")
        if describe:
            info_json = describe_spec(deployment_spec)
            pprint(info_json)
    except BCDTBaseException:
        # todo: handle all possible exceptions and show proper errors to user
        raise


@bcdt.command()
@click.argument("deployment_spec", type=click.Path())
def update(deployment_spec, name, bento_bundle, operator):
    """
    Update deployments.
    """
    update_spec(deployment_spec_path=deployment_spec)


@bcdt.command()
@click.argument("deployment_spec", type=click.Path())
def delete(deployment_spec, name, operator):
    """
    Delete the deployments made.
    """
    delete_spec(deployment_spec_path=deployment_spec)


@bcdt.command()
@click.argument("deployment_spec", type=click.Path())
def describe(deployment_spec, name, operator):
    """
    Shows the discription any deployment made.
    """
    describe_spec(deployment_spec_path=deployment_spec)


# subcommands
bcdt.add_command(get_operator_management_subcommands())
