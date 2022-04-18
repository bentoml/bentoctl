from rich.console import Console

console = Console(highlight=False)


def print_generated_files_list(generated_files: list):
    console.print(":sparkles: generated template files.")
    for file in generated_files:
        console.print(f"  - {file}")


def prompt_user_for_filename():
    deployment_config_filname = console.input(
        "filename for deployment_config [[b]deployment_config.yaml[/]]: ",
    )
    if deployment_config_filname == "":
        deployment_config_filname = "deployment_config.yaml"

    if not (
        deployment_config_filname.endswith(".yaml")
        or deployment_config_filname.endswith(".yml")
    ):
        deployment_config_filname += ".yaml"

    return deployment_config_filname
