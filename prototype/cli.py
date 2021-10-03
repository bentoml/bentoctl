import click
import time


@click.group()
def functional():
    pass


@click.group()
def management():
    pass


@functional.command()
@click.argument("config_file_path")
def deploy(config_file_path):
    print(f"loading config from {config_file_path}")
    print("Deploying to cloud...")


@functional.command()
@click.argument("config_file_path")
def describe(config_file_path):
    print(f"loading config from {config_file_path}")
    print("describe deployment")


@functional.command()
@click.argument("config_file_path")
def update(config_file_path):
    print(f"loading config from {config_file_path}")
    print("update deployment")


@functional.command()
@click.argument("config_file_path")
def delete(config_file_path):
    print(f"loading config from {config_file_path}")
    print("delete deployment")


if __name__ == "__main__":
    functional()
