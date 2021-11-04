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
        while True:
            val = prompt(field, rule.get("default"))
            validated_field = v.validated({field: val}, schema={field: rule})
            if validated_field is None:
                error_str = "\n".join(v.errors[field])
                console.print(f"[red]{error_str}[/]")
            else:
                spec.update(validated_field)
                intended_print(f"{field}: {validated_field[field]}", indent=1)
                break

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
