import click
from bcdt.cli.deployer_management import get_deployer_management_subcommands
from bcdt.ops import deploy_bundle, describe_deployment, delete_deployment, update_deployment


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
    "--deployer", "-d", type=click.STRING, help="The deployer of choice to deploy"
)
@click.argument("bento_bundle")
def deploy(bento_bundle, name, config, deployer):
    """
    Deploy a bentoml bundle to cloud.
    """
    print("deploying")
    deploy_bundle(bento_bundle, name, config, deployer)


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
    "--deployer", "-d", type=click.STRING, help="The deployer of choice to deploy"
)
def delete(name, config, deployer):
    print("deleting")
    delete_deployment(name, config, deployer)


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
    "--deployer", "-d", type=click.STRING, help="The deployer of choice to deploy"
)
def describe(name, config, deployer):
    describe_deployment(name, config, deployer)


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
    "--deployer", "-d", type=click.STRING, help="The deployer of choice to deploy"
)
@click.argument('bento_bundle', type=click.STRING)
def update(bento_bundle, name, config, deployer):
    update_deployment(bento_bundle, name, config, deployer)


bcdt.add_command(get_deployer_management_subcommands())
