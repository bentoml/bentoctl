import readline
import sys

from pathlib import Path

import cerberus
import click
import yaml
from simple_term_menu import TerminalMenu

from bcdt.operator import LocalOperatorManager, Operator
from bcdt.utils import console



def choose_operator_from_list():
    """
    interactive menu to select operator
    """
    available_operators = list(LocalOperatorManager.list())
    tmenu = TerminalMenu(available_operators, title="Choose an operator")
    choice = tmenu.show()
    return available_operators[choice]


def _input_with_default_value(prompt, default_value=None):
    def hook():
        def _hook():
            readline.insert_text(str(default_value))
            readline.redisplay()

        if default_value is None:
            return None
        else:
            return _hook

    readline.set_pre_input_hook(hook())
    result = input(prompt)
    readline.set_pre_input_hook()

    if result == "":
        return None
    return result


def prompt(field, default=None, help_str=None):
    default_str = "" if default is None else f"[[b]{default}[/]]"
    if help_str is not None:
        console.print(f"({help_str})")
    value = console.input(f"{field} {default_str}: ")

    screen_code = "\033[1A[\033[2K"
    print(screen_code, end="")
    return value if value != "" else None


def prompt_input(validator, rule, field, default=None, help_message=None):
    def find_how_many_lines(string_to_print):
        return 1

    line_to_remove = 0
    default_str = "" if default is None else f"[[b]{default}[/]]"
    if help_message is not None:
        lines_to_print = find_how_many_lines(help_message)
        console.print(f"({help_message})")
        line_to_remove += lines_to_print
    value = console.input(f"{field} {default_str}: ")
    line_to_remove += 1
    validated_field = validator.validated({field: value}, schema={field: rule})
    ## TODO: fix this @jithin
    if validated_field is None:
        error_str = "\n".join(validator.errors[field])
        line_to_remove += find_how_many_lines(error_str)
        console.print(f"[red]{error_str}[/]")

    screen_code = "\033[1A[\033[2K"
    while line_to_remove > 0:
        print(screen_code, end="")
        line_to_remove -= 1
    return value


def intended_print(string, indent=0):
    indent = "    " * indent
    console.print(indent, end="")
    console.print(string)


def generate_metadata(bento, name, operator):
    console.print("[bold]metadata: [/]")
    if name is None:
        name = prompt("Deployment name")
    intended_print(f"name: {name}", indent=1)
    if operator is None:
        operator = choose_operator_from_list()
    intended_print(f" operator: {operator}", indent=1)
    if bento is None:
        bento = prompt("bento")
    intended_print(f"bento: {bento}", indent=1)

    return {"name": name, "operator": operator, "bento": bento}


def deployment_spec_builder(bento=None, name=None, operator=None):
    """
    Interactively build the deployment spec.
    """
    console.print("[r]Interactive Deployment Spec Builder[/]")
    console.print(
        """
[green]Welcome![/] You are now in interactive mode.

This mode will help you setup the deployment_spec.yaml file required for
deployment. Fill out the appropriate values for the fields.

[dim]\[deployment spec will be saved to: ./deployment_spec.yaml][/]
"""
    )

    console.print("[b]api_version:[/] v1")
    metadata = generate_metadata(bento, name, operator)

    op_path, _ = LocalOperatorManager.get(metadata["operator"])
    op = Operator(op_path)
    v = cerberus.Validator()
    spec = {}
    console.print("[bold]spec: [/]")
    for field, rule in op.operator_schema.items():
        value = prompt_input(v, rule, field, help_message=rule.get("help"))
        spec.update({field: value})
        intended_print(f"{field}: {value}", indent=1)

    print()  # blank line to sperate

    deployment_spec = {"api_version": "v1", "metadata": metadata, "spec": spec}
    return deployment_spec


def save_deployment_spec(deployment_spec, save_path, filename="deployment_spec.yaml"):
    spec_path = Path(save_path, filename)

    if spec_path.exists():
        overide = click.confirm(
            "deployment spec file exists! Should I overide?", default=True
        )

        if overide:
            spec_path.unlink()
        else:
            return spec_path

    with open(spec_path, "w") as f:
        yaml.dump(deployment_spec, f)

    return spec_path
