import click


@click.group()
def cli():
    ...


@cli.command()  # @cli, not @click!
def sync():
    print("group 1")


@click.group()
def cli2():
    pass


@cli.command()
def another():
    print("group 2")


if __name__ == "__main__":
    cli()
