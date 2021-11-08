import readline
import sys
from pathlib import Path

import cerberus
import click
import yaml
from rich.control import Control
from rich.segment import ControlType, SegmentLines
from simple_term_menu import TerminalMenu

from bcdt.deployment_spec import metadata_schema
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


class PromptMsg:
    def __init__(self, help_msg, val_error=None):
        self.help_msg = help_msg
        self.val_error = val_error

    def __rich_console__(self, console, options):
        if self.help_msg is not None:
            yield f"[grey50]Help: {self.help_msg}[/]"
        if self.val_error is not None:
            yield f"[red]Validation Error: {self.val_error}[/]"


def clear_console(num_lines):
    """Clears the number of lines"""
    console.print(
        Control(
            ControlType.CARRIAGE_RETURN,
            (ControlType.ERASE_IN_LINE, 2),
            *(
                (
                    (ControlType.CURSOR_UP, 1),
                    (ControlType.ERASE_IN_LINE, 2),
                )
                * num_lines
            ),
        )
    )


def prompt_input(field, rule):
    validator = cerberus.Validator()
    validation_error_msg = None
    help_message = rule.pop("help_message", None)
    default = rule.get("default")
    default_str = "" if default is None else f"[[b]{default}[/]]"
    while True:
        prompt_msg_lines = console.render_lines(
            PromptMsg(help_message, validation_error_msg)
        )
        num_lines = len(prompt_msg_lines)
        console.print(SegmentLines(prompt_msg_lines, new_lines=True))
        value = console.input(f"{field} {default_str}: ")
        clear_console(num_lines + 1)
        value = value if value != "" else None
        validated_field = validator.validated({field: value}, schema={field: rule})
        if validated_field is None:
            validation_error_msg = ". ".join(validator.errors[field])
        else:
            return validated_field[field]


def intended_print(string, indent=0):
    indent = "    " * indent
    console.print(indent, end="")
    console.print(string)


def generate_metadata(bento, name, operator):
    if name is None:
        name = prompt_input("name", metadata_schema.get("name"))
    intended_print(f"name: {name}", indent=1)
    if operator is None:
        operator = choose_operator_from_list()
    intended_print(f"operator: {operator}", indent=1)
    if bento is None:
        bento = prompt_input("bento", metadata_schema.get("bento"))
    intended_print(f"bento: {bento}", indent=1)

    return {"name": name, "operator": operator, "bento": bento}


def generate_spec(schema):
    spec = {}
    for field, rule in schema.items():
        val = prompt_input(field, rule)
        spec.update({field: val})
        intended_print(f"{field}: {val}", indent=1)


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

    # api_version
    console.print("[b]api_version:[/] v1")

    # metadata
    console.print("[bold]metadata: [/]")
    metadata = generate_metadata(bento, name, operator)

    # spec
    console.print("[bold]spec: [/]")
    op_path, _ = LocalOperatorManager.get(metadata["operator"])
    op = Operator(op_path)
    spec = generate_spec(op.operator_schema)

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
