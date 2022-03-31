import sys
import os
from pathlib import Path

import click
import yaml

from bentoctl import __version__
from bentoctl.cli.interactive import deployment_config_builder
from bentoctl.cli.operator_management import get_operator_management_subcommands
from bentoctl.cli.utils import BentoctlCommandGroup
from bentoctl.deployment_config import DeploymentConfig
from bentoctl.exceptions import BentoctlException
from bentoctl.utils import TempDirectory, console
from bentoctl.docker_utils import build_docker_image, push_docker_image_to_repository

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


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


@click.group(
    context_settings=CONTEXT_SETTINGS,
    cls=BentoctlCommandGroup,
)
@click.version_option(version=__version__)
def bentoctl():
    """
    Bentoctl - Manages deployment of bentos to various cloud services.

    This tool helps you deploy your bentos to any cloud service you want. To start off
    you have to install some operators that you need to deploy to the cloud
    service of your choice, check out `bentoctl operator --help` for more details.
    You can run `bentoctl generate` to start the interactive deployment config builder
    or check out the <link to deployment_config doc> on how to write one yourself.
    """


@bentoctl.command()
@click.option("--file", "-f", type=click.File(), help="Path to the deployment config file.")
@click.option("--generate/--not-generate", default=True, help="Generate a deployment config.")
@click.option("--save-path", help="Path to save the deployment config file.", default=".")
def init(file, save_path, generate):
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
            file = save_deployment_config(
                deployment_config, Path.cwd(), deployment_config_filname
            )
            console.print(
                "[green]deployment config generated to: "
                f"{file.relative_to(Path.cwd())}[/]"
            )
        deployment_config = DeploymentConfig.from_file(file)
        if generate:
            deployment_config.generate()
    except BentoctlException as e:
        console.print(f"[red]{e}[/]")
        sys.exit(1)


@bentoctl.command()
@click.option("--deployment-config-file", "-f", default="deployment_config.yaml", help="path to deployment config file")
@click.option("--values-only", is_flag=True, help="only update values")
def generate(deployment_config_file, values_only):
    """
    Generate the files for the deployment based on the template type provided.
    """
    deployment_config = DeploymentConfig.from_file(deployment_config_file)
    deployment_config.generate(values_only)


@bentoctl.command()
@click.option("--bento-tag", "-b", help="Bento tag to use for deployment.", required=True)
@click.option("--deployment_config_file", "-f", help="path to deployment_config file", required=True)
@click.option("--push", is_flag=True, default=False)
@click.option("--debug", is_flag=True, default=False)
def build(
    bento_tag,
    deployment_config_file,
    push,
    debug,
):
    """
    Build the Docker image to deploy to the cloud. Pass the `--push` flag to push it
    into the default registry.
    """
    deployment_config = DeploymentConfig.from_file(deployment_config_file)
    deployment_config.set_bento(bento_tag)
    with TempDirectory() as dist_dir:
        (
            dockerfile_path,
            dockercontext_path,
            build_args,
        ) = deployment_config.create_deployable(
            destination_dir=dist_dir,
            overwrite_deployable=debug,
        )
        (registry_url, registry_username, registry_password) = deployment_config.get_registry_info()

        image_tag = deployment_config.generate_docker_image_tag(registry_url)

        build_docker_image(
            image_tag=image_tag,
            context_path=dockercontext_path,
            dockerfile=dockerfile_path,
            additional_build_args=build_args,
        )

    if push:
        push_docker_image_to_repository(
            repository=image_tag, username=registry_username, password=registry_password
        )
    deployment_config.generate()

# subcommands
bentoctl.add_command(get_operator_management_subcommands())
