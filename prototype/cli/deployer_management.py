import click


def get_deployer_management_subcommands():
    @click.group(name="deployers")
    def deployer_management():
        pass

    @deployer_management.command()
    def list():
        print("list all commands")

    @deployer_management.command()
    def add():
        print("adding deployer")

    @deployer_management.command()
    def remove():
        print("removing deployer")

    return deployer_management
