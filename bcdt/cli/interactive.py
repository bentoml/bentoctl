import readline
from pathlib import Path

import cerberus
import click
import yaml

from bcdt.operator import LocalOperatorManager, Operator


def choose_operator_from_list():
    """
    interactive
    """
    available_operators = LocalOperatorManager.list().keys()
    print("Available operators:")
    print("\n".join(available_operators))
    operator_name = input("operator name of choice: ")

    assert (
        operator_name in available_operators
    ), f"{operator_name} not in available operators list"

    return operator_name


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


def generate_metadata(bento_bundle, name, operator):
    if bento_bundle is None:
        bento_bundle = click.prompt("Path to bento bundle", type=click.Path())
    if name is None:
        name = click.prompt("Deployment name")
    if operator is None:
        operator = choose_operator_from_list()

    return {"name": name, "operator": operator, "bento_bundle": bento_bundle}


def deployment_spec_builder(bento_bundle, name, operator):
    """
    Interactively build the deployment spec.
    """
    metadata = generate_metadata(bento_bundle, name, operator)
    op_path, _ = LocalOperatorManager.get(metadata["operator"])
    op = Operator(op_path)
    v = cerberus.Validator()
    spec = {}
    for field, rule in op.operator_schema.items():
        while True:
            val = _input_with_default_value(f"{field} : ", rule.get("default"))
            validated_field = v.validated({field: val}, schema={field: rule})
            if validated_field is None:
                print(f"value is incorrect: {v.errors}")
            else:
                spec.update(validated_field)
                break

    deployment_spec = {"api_version": "v1", "metadata": metadata, "spec": spec}
    return deployment_spec


def save_deployment_spec(deployment_spec, save_path, filename="deployment_spec.yaml"):
    spec_path = Path(save_path, filename)

    if spec_path.exists():
        overide = click.confirm("deployment spec file exists! Should I overide?")
        if overide:
            spec_path.unlink()
        else:
            return spec_path

    with open(spec_path, "w") as f:
        yaml.dump(deployment_spec, f)

    return spec_path
