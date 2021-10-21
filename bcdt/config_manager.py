import json
import readline
from pathlib import Path
from typing import List, Dict

import yaml

from .operator_manager import get_operator_list
from .operator_loader import Operator


def load_json_config(config_path):
    config_dict = json.loads(config_path.read_text())

    return config_dict


def load_yaml_config(config_path):
    config_dict = yaml.safe_load(config_path.read_text())

    return config_dict


def dump_yaml_config(data, yaml_path):
    with open(yaml_path, 'w') as f:
        yaml.dump(data, f)


def parse_config_file(config_file):
    if config_file.suffix == ".json":
        config_dict = json.loads(config_file.read_text())
    elif config_file.suffix in [".yaml", ".yml"]:
        config_dict = yaml.safe_load(config_file.read_text())
    else:
        raise Exception("Incorrect config file")

    # currently there is only 1 version for config
    assert config_dict['apiVersion'] == 'v1'

    return config_dict['spec']


def fill_defaults(configs, default_config):
    """
    Fill out all the required and default configs for the selected deployment into
    `configs`
    """
    config_dict = {}
    for k, v in default_config.items():
        if k not in configs and v == "":
            value = input(f"Enter value for {k}: ")
            config_dict[k] = value
        elif k not in configs:
            config_dict[k] = v
        else:
            config_dict[k] = configs[k]

    configs["config_dict"] = config_dict
    return configs


def choose_operator():
    available_operators = get_operator_list().keys()
    print("Available operators:")
    print("\n".join(available_operators))
    operator_name = input("operator name of choice: ")

    assert (
        operator_name in available_operators
    ), f"{operator_name} not in available operators list"

    return operator_name


def _input_with_prefill(prompt, default_value):
    def hook():
        readline.insert_text(str(default_value))
        readline.redisplay()

    readline.set_pre_input_hook(hook)
    result = input(prompt)
    readline.set_pre_input_hook()
    return result


def fill_required_fields(required_fields: List):
    required_vals = {}

    for field in required_fields:
        required_vals[field] = input(f"{field }: ")

    return required_vals


def fill_defaults_fields(default_fields: Dict):
    for field in default_fields:
        default_fields[field] = _input_with_prefill(f"{field}: ", default_fields[field])

    return default_fields


def _validate_spec(spec: Dict, required_fields: List, default_fields: Dict):
    """
    Validates the spec from the config file to make sure the required_fields are
    present. It also populates the spec with default_fields that are not present in the
    config file provided.
    """
    for field in required_fields:
        if field not in spec:
            raise ValueError(f"The required field '{field}' is not provided in spec.")

    for field, val in default_fields.items():
        if field not in spec:
            spec[field] = val

    return spec


def build_config_dict(metadata):
    """
    Build the config_dict needed for deployment to the provided service. Prompt the
    user for configs that are required but not provided and use the default configs
    from the operator to populate all the others.
    """
    if metadata["deployment_name"] is None:
        metadata["deployment_name"] = input("Enter a Name for deployment: ")

    if metadata["operator_name"] is not None:
        operator_name = metadata["operator_name"]
    else:
        operator_name = choose_operator()
        metadata["operator_name"] = operator_name

    # lets load the spec
    operator_list = get_operator_list()
    operator = Operator(operator_list[operator_name])
    if metadata["config_path"] is not None:
        config_path = Path(metadata["config_path"])

        if not config_path.exists():
            raise FileNotFoundError(
                "the config file {} is not found!".format(config_path)
            )

        spec = parse_config_file(config_path)
        spec = _validate_spec(spec, operator.required_fields, operator.default_fields)
    else:  # user provided no config file
        # load required and default args
        required_fields = fill_required_fields(operator.required_fields)
        default_fields = fill_defaults_fields(operator.default_fields)
        spec = {**required_fields, **default_fields}

    return metadata, spec
