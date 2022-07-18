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


POST_BUILD_HELP_MESSAGE_TERRAFORM = """
bentoctl has built and pushed the bento and generated the terraform files 🎉

Now follow the steps below to use terraform to carry out the deployment
1. Initialise the terraform working directory.
$ terraform init

2. Run terraform plan to see the changes that will take place
$ terraform plan -var-file bentoctl.tfvars

3. Apply the changes to create the actual infrastructure
$ terraform apply -var-file bentoctl.tfvars

To cleanup all the resources and delete the repositories created run
$ bentoctl destroy

---
There is also an experimental command that you can use.
To create the resources specifed run this after the build command.
$ bentoctl apply

To cleanup all the resources created and delete the registry run
$ bentoctl destroy
"""


def print_post_build_help_message(template_type: str):
    if template_type.startswith("terraform"):
        console.print(f"[green]{POST_BUILD_HELP_MESSAGE_TERRAFORM}[/green]")
