import os

import click

from bentoctl import __version__
from bentoctl.cli.interactive import deployment_config_builder
from bentoctl.cli.operator_management import get_operator_management_subcommands
from bentoctl.cli.utils import BentoctlCommandGroup, handle_bentoctl_exceptions
from bentoctl.console import (
    console,
    print_generated_files_list,
    print_post_build_help_message,
    prompt_user_for_filename,
)
from bentoctl.deployment_config import DeploymentConfig
from bentoctl.docker_utils import (
    generate_deployable_container,
    push_docker_image_to_repository,
    tag_docker_image,
)
from bentoctl.utils import is_debug_mode
from bentoctl.utils.terraform import (
    is_terraform_applied,
    terraform_apply,
    terraform_destroy,
)

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(
    context_settings=CONTEXT_SETTINGS,
    cls=BentoctlCommandGroup,
)
@click.version_option(version=__version__)
def bentoctl():
    """
    Bentoctl - Fast model deployment on any cloud platform

    bentoctl is a CLI tool for deploying your machine-learning models to any cloud
    platforms and serving predictions via REST APIs. It is built on top of
    BentoML: the unified model serving framework, and makes it easy to bring any BentoML
    packaged model to production.
    """


@bentoctl.command()
@click.option(
    "--do-not-generate",
    is_flag=True,
    default=False,
    help="Generate template files based on the provided operator.",
)
@click.option(
    "--save-path",
    help="Path to save the deployment config file.",
    type=click.Path(exists=True, file_okay=False),
    default=os.curdir,
)
@handle_bentoctl_exceptions
def init(save_path, do_not_generate):
    """
    Start the interactive deployment config builder file.
    """
    deployment_config = deployment_config_builder()
    deployment_config_filname = prompt_user_for_filename()

    config_path = os.path.join(save_path, deployment_config_filname)
    if os.path.exists(config_path):
        if click.confirm(
            "deployment config file exists! Should I override?", default=True
        ):
            os.remove(config_path)
        else:
            return

    deployment_config.save(save_path=save_path, filename=deployment_config_filname)
    try:
        relative_path = os.path.relpath(config_path, os.curdir)
    except ValueError:
        relative_path = config_path
    console.print("[green]deployment config generated to: " f"{relative_path}[/]")

    if not do_not_generate:
        generated_files = deployment_config.generate(destination_dir=save_path)
        print_generated_files_list(generated_files)
    return deployment_config


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
@handle_bentoctl_exceptions
def generate(deployment_config_file, values_only, save_path):
    """
    Generate template files for deployment.
    """
    deployment_config = DeploymentConfig.from_file(deployment_config_file)
    generated_files = deployment_config.generate(
        destination_dir=save_path, values_only=values_only
    )
    print_generated_files_list(generated_files)
    return deployment_config


@bentoctl.command()
@click.option(
    "--bento-tag", "-b", help="Bento tag to use for deployment.", required=True
)
@click.option(
    "--deployment-config-file",
    "-f",
    help="path to deployment_config file",
    default="deployment_config.yaml",
)
@click.option("--dry-run", is_flag=True, help="Dry run", default=False)
@handle_bentoctl_exceptions
def build(
    bento_tag,
    deployment_config_file,
    dry_run,
):
    """
    Build the Docker image for the given deployment config file and bento.
    """

    deployment_config = DeploymentConfig.from_file(deployment_config_file)
    deployment_config.set_bento(bento_tag)
    local_docker_tag = deployment_config.generate_local_image_tag()

    generate_deployable_container(
        tag=local_docker_tag,
        deployment_config=deployment_config,
        cleanup=False if is_debug_mode() else True,
    )

    if not dry_run:
        (
            repository_url,
            username,
            password,
        ) = deployment_config.create_repository()

        console.print(f"Created the repository {deployment_config.repository_name}")
        repository_image_tag = deployment_config.generate_docker_image_tag(
            repository_url
        )
        tag_docker_image(local_docker_tag, repository_image_tag)
        push_docker_image_to_repository(
            repository=repository_image_tag,
            username=username,
            password=password,
        )
        generated_files = deployment_config.generate(values_only=True)
        print_generated_files_list(generated_files)
        print_post_build_help_message(template_type=deployment_config.template_type)
    else:
        console.print(f"[green]Created docker image: {local_docker_tag}[/]")
    return deployment_config


@bentoctl.command()
@click.option(
    "--deployment-config-file",
    "-f",
    help="path to deployment_config file",
    default="deployment_config.yaml",
)
@handle_bentoctl_exceptions
def destroy(deployment_config_file):
    """
    Destroy all the resources created and remove the registry.
    """
    deployment_config = DeploymentConfig.from_file(deployment_config_file)
    if (
        deployment_config.template_type.startswith("terraform")
        and is_terraform_applied()
    ):
        terraform_destroy()
    deployment_config.delete_repository()
    console.print(f"Deleted the repository {deployment_config.repository_name}")
    return deployment_config


@bentoctl.command()
@click.option(
    "--deployment-config-file",
    "-f",
    help="path to deployment_config file",
    default="deployment_config.yaml",
)
@handle_bentoctl_exceptions
def apply(deployment_config_file):
    """
    [Experimental] Apply the generated template file to create/update the deployment.
    """
    deployment_config = DeploymentConfig.from_file(deployment_config_file)
    if deployment_config.template_type.startswith("terraform"):
        terraform_apply()

    return deployment_config


# subcommands
bentoctl.add_command(get_operator_management_subcommands())
