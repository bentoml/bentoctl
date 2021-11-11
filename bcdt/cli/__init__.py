from pathlib import Path

import click
import cloup
from cloup import Section
from rich.pretty import pprint

from bcdt.cli.interactive import deployment_spec_builder, save_deployment_spec
from bcdt.cli.operator_management import get_operator_management_subcommands
from bcdt.deployment_spec import DeploymentSpec
from bcdt.exceptions import BCDTBaseException
from bcdt.ops import delete_spec, deploy_spec, describe_spec, update_spec
from bcdt.utils import console

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


class BcdtSections:
    OPERATIONS = Section("Deployment Operations")
    OPERATORS = Section("Operator Management")
    INTERACTIVE = Section("Interactive Mode")


@cloup.group(show_subcommand_aliases=True, context_settings=CONTEXT_SETTINGS)
def bcdt():
    """
    <name> (bcdt) - Manages deployment of bentos to various cloud services.

    This tool helps you deploy your bentos to any cloud service you want. To start off
    you have to install some operators that you need to deploy to the cloud
    service of your choice, check out `bcdt operator --help` for more details. You can
    run `bcdt generate` to start the interactive deployment spec builder or
    check out the <link to deployment_spec doc> on how to write one yourself.
    """
    pass


@bcdt.command(section=BcdtSections.OPERATIONS)
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
    Deploy a bento to cloud either in interactive mode or with deployment_spec.

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


@bcdt.command(section=BcdtSections.OPERATIONS)
@click.argument("deployment_spec", type=click.Path())
def describe(deployment_spec, name, operator):
    """
    Shows the properties of the deployment given a deployment_spec.
    """
    describe_spec(deployment_spec_path=deployment_spec)


@bcdt.command(section=BcdtSections.OPERATIONS)
@click.argument("deployment_spec", type=click.Path())
def update(deployment_spec, name, bento, operator):
    """
    Update the deployment given a deployment_spec.
    """
    update_spec(deployment_spec_path=deployment_spec_path)


@bcdt.command(section=BcdtSections.OPERATIONS)
@click.argument("deployment_spec", type=click.Path())
def delete(deployment_spec, name, operator):
    """
    Delete the deployment given a deployment_spec.
    """
    deployment_name = delete_spec(deployment_spec_path=deployment_spec_path)
    click.echo(f"Deleted deployment - {deployment_name}!")


@bcdt.command(section=BcdtSections.INTERACTIVE)
def generate():
    """
    Start the interactive deployment spec builder file.
    """
    deployment_spec = deployment_spec_builder()
    dspec = DeploymentSpec(deployment_spec)
    spec_path = save_deployment_spec(dspec.deployment_spec, Path.cwd())
    console.print(
        f"[green]deployment spec generated to: {spec_path.relative_to(Path.cwd())}[/]"
    )


# subcommands
bcdt.add_command(get_operator_management_subcommands(), section=BcdtSections.OPERATORS)
