from pathlib import Path

import click
import cloup
from rich.pretty import pprint

from bcdt.cli.interactive import deployment_spec_builder, save_deployment_spec
from bcdt.cli.operator_management import get_operator_management_subcommands
from bcdt.deployment_spec import DeploymentSpec
from bcdt.exceptions import BCDTBaseException
from bcdt.ops import delete_spec, deploy_spec, describe_spec, update_spec
from bcdt.utils import console


@cloup.group(show_subcommand_aliases=True)
def bcdt():
    pass


@bcdt.command()
def generate():
    """
    Generate the deployment spec file.
    """
    deployment_spec = deployment_spec_builder()
    dspec = DeploymentSpec(deployment_spec)
    spec_path = save_deployment_spec(dspec.deployment_spec, Path.cwd())
    console.print(
        f"[green]deployment spec generated to: {spec_path.relative_to(Path.cwd())}[/]"
    )


@bcdt.command()
@click.option(
    "--name", "-n", type=click.STRING, help="The name you want to give the deployment"
)
@click.option(
    "--operator", "-o", type=click.STRING, help="The operator of choice to deploy"
)
@click.option(
    "--bento", "-b", type=click.STRING, help="The path to bento bundle.",
)
@click.option("--describe", is_flag=True)
@click.argument("deployment_spec_path", type=click.Path(), required=False)
def deploy(deployment_spec_path, name, operator, bento, describe):
    """
    Deploy a bentoml bundle to cloud.

    1. if interactive mode. call the interactive setup manager
    2. call deploy_bento
    3. display results from deploy_bento
    """
    try:
        if deployment_spec_path is None:
            deployment_spec = deployment_spec_builder(bento, name, operator)
            dspec = DeploymentSpec(deployment_spec)
            deployment_spec_path = save_deployment_spec(
                dspec.deployment_spec, Path.cwd()
            )
            console.print(
                "[green]deployment spec generated to: "
                f"{deployment_spec_path.relative_to(Path.cwd())}[/]"
            )
        deploy_spec(deployment_spec_path)
        print("Successful deployment!")
        if describe:
            info_json = describe_spec(deployment_spec_path)
            pprint(info_json)
    except BCDTBaseException as e:
        e.show()


@bcdt.command()
@click.argument("deployment_spec_path", type=click.Path())
def update(deployment_spec_path):
    """
    Update deployments.
    """
    update_spec(deployment_spec_path=deployment_spec_path)

@bcdt.command()
@click.argument("deployment_spec_path", type=click.Path())
def delete(deployment_spec_path):
    """
    Delete the deployments made.
    """
    deployment_name = delete_spec(deployment_spec_path=deployment_spec_path)
    click.echo(f"Deleted deployment - {deployment_name}!")


@bcdt.command()
@click.argument("deployment_spec_path", type=click.Path())
def describe(deployment_spec_path):
    """
    Shows the discription any deployment made.
    """
    info_json = describe_spec(deployment_spec_path=deployment_spec_path)
    pprint(info_json)


# subcommands
bcdt.add_command(get_operator_management_subcommands())
