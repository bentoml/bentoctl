import os
import sys

import click
import yaml

from bentoctl import __version__
from bentoctl.cli.interactive import deployment_config_builder
from bentoctl.cli.operator_management import get_operator_management_subcommands
from bentoctl.cli.utils import BentoctlCommandGroup
from bentoctl.console import print_generated_files_list
from bentoctl.deployment_config import DeploymentConfig
from bentoctl.docker_utils import build_docker_image, push_docker_image_to_repository
from bentoctl.exceptions import BentoctlException
from bentoctl.utils import TempDirectory, console

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


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
@click.option(
    "--generate/--no-generate",
    default=True,
    help="Generate template files based on the provided operator.",
)
@click.option(
    "--save-path",
    help="Path to save the deployment config file.",
    type=click.Path(exists=True, file_okay=False),
    default=os.curdir,
)
def init(save_path, generate):
    """
    Start the interactive deployment config builder file.

    Initialize a deployment configuration file using interactive mode.
    """
    try:
        deployment_config = deployment_config_builder()
        deployment_config_filname = console.input(
            "filename for deployment_config [[b]deployment_config.yaml[/]]: ",
        )
        config_path = os.path.join(save_path, deployment_config_filname)

        if os.path.exists(config_path):
            override = click.confirm(
                "deployment config file exists! Should I override?", default=True
            )
            if override:
                os.remove(config_path)
            else:
                return

        with open(config_path, "w", encoding="UTF-8") as f:
            yaml.safe_dump(deployment_config, f, default_flow_style=False, sort_keys=False)
        console.print(
            "[green]deployment config generated to: "
            f"{os.path.relpath(config_path, save_path)}[/]"
        )

        if generate:
            generated_files = deployment_config.generate()
            print_generated_files_list(generated_files)
    except BentoctlException as e:
        console.print(f"[red]{e}[/]")
        sys.exit(1)


@bentoctl.command()
@click.option(
    "--deployment-config-file",
    "-f",
    default="deployment_config.yaml",
    help="path to deployment config file",
)
@click.option(
    "--save-path",
    help="Path to save the deployment config file.",
    type=click.Path(exists=True, file_okay=False),
    default=os.curdir,
)
@click.option(
    "--values-only",
    is_flag=True,
    help="create/update the values file only.",
    default=False,
)
def generate(deployment_config_file, values_only, save_path):
    """
    Generate template files for deployment.
    """
    deployment_config = DeploymentConfig.from_file(deployment_config_file)
    generated_files = deployment_config.generate(
        destination_dir=save_path, values_only=values_only
    )
    print_generated_files_list(generated_files)


@bentoctl.command()
@click.option(
    "--bento-tag", "-b", help="Bento tag to use for deployment.", required=True
)
@click.option("--operator", "-op", help="The operator used to build the Image")
@click.option(
    "--deployment_config_file",
    "-f",
    help="path to deployment_config file",
    required=True,
)
@click.option("--push/--no-push", default=False)
def build(
    bento_tag,
    operator,
    deployment_config_file,
    push,
):
    """
    Build the Docker image to deploy to the cloud.

    Pass the `--push` flag to push it into the default registry.
    """
    if deployment_config_file is not None:
        deployment_config = DeploymentConfig.from_file(deployment_config_file)
    elif operator is not None:
        deployment_config = DeploymentConfig()

    deployment_config.set_bento(bento_tag)
    with TempDirectory() as dist_dir:
        (
            dockerfile_path,
            dockercontext_path,
            build_args,
        ) = deployment_config.create_deployable(
            destination_dir=dist_dir,
        )
        (
            registry_url,
            registry_username,
            registry_password,
        ) = deployment_config.get_registry_info()

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
    generated_files = deployment_config.generate(values_only=True)
    print_generated_files_list(generated_files)


# subcommands
bentoctl.add_command(get_operator_management_subcommands())
