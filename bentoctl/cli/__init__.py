import sys
from pathlib import Path

import click
import cloup
import yaml
from cloup import Section

from bentoctl import __version__
from bentoctl.cli.interactive import deployment_config_builder
from bentoctl.cli.operator_management import get_operator_management_subcommands
from bentoctl.cli.utils import BentoctlCommandGroup
from bentoctl.deployment_config import DeploymentConfig
from bentoctl.exceptions import BentoctlException
from bentoctl.utils import console

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


class BentoctlSections:
    OPERATIONS = Section("Deployment Operations")
    OPERATORS = Section("Operator Management")
    INTERACTIVE = Section("Interactive Mode")


def save_deployment_config(
    deployment_config, save_path, filename="deployment_config.yaml"
):
    config_path = Path(save_path, filename)

    if config_path.exists():
        override = click.confirm(
            "deployment config file exists! Should I override?", default=True
        )
        if override:
            config_path.unlink()
        else:
            return config_path

    with open(config_path, "w", encoding="UTF-8") as f:
        yaml.safe_dump(deployment_config, f, default_flow_style=False, sort_keys=False)

    return config_path


@cloup.group(
    show_subcommand_aliases=True,
    context_settings=CONTEXT_SETTINGS,
    cls=BentoctlCommandGroup,
)
@cloup.version_option(version=__version__)
def bentoctl():
    """
    Bentoctl - Manages deployment of bentos to various cloud services.

    This tool helps you deploy your bentos to any cloud service you want. To start off
    you have to install some operators that you need to deploy to the cloud
    service of your choice, check out `bentoctl operator --help` for more details.
    You can run `bentoctl generate` to start the interactive deployment config builder
    or check out the <link to deployment_config doc> on how to write one yourself.
    """


@bentoctl.command(section=BentoctlSections.INTERACTIVE)
@click.option('--file', '-f', help='Path to the deployment config file.')
def init(file):
    """
    Start the interactive deployment config builder file.
    Initialize a deployment configuration file using interactive mode.
    """
    try:
        if file is None:
            deployment_config = deployment_config_builder()
            deployment_config_filname = console.input(
                "filename for deployment_config [[b]deployment_config.yaml[/]]: ",
            )
            if deployment_config_filname == "":
                deployment_config_filname = "deployment_config.yaml"
            config_path = save_deployment_config(
                deployment_config, Path.cwd(), deployment_config_filname
            )
            console.print(
                "[green]deployment config generated to: "
                f"{config_path.relative_to(Path.cwd())}[/]"
            )
        deployment_config = DeploymentConfig(file)
        deployment_config.generate()
    except BentoctlException as e:
        console.print(f"[red]{e}[/]")
        sys.exit(1)

@bentoctl.command(section=BentoctlSections.OPERATIONS)
def build():
    # operator.create_deployable()
    # build_docker_image()
    # push_docker_image_to_repository()
    # generate_bentoctl_files()
    pass


# subcommands
bentoctl.add_command(
    get_operator_management_subcommands(), section=BentoctlSections.OPERATORS
)
