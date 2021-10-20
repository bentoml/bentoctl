import json
from pathlib import Path

import yaml

from .operator_manager import get_operator_list
from .operator_loader import Operator


def load_json_config(config_path):
    config_dict = json.loads(config_path.read_text())

    return config_dict


def load_yaml_config(config_path):
    config_dict = yaml.safe_load(config_path.read_text())

    return config_dict


def parse_config_file(config_file):
    if config_file.suffix == ".json":
        config_dict = json.loads(config_file.read_text())
    elif config_file.suffix in [".yaml", ".yml"]:
        config_dict = yaml.safe_load(config_file.read_text())
    else:
        raise Exception("Incorrect config file")

    config_dict["deployment_name"] = config_dict["name"]
    config_dict["operator_name"] = config_dict["operator"]

    return config_dict


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

    configs['config_dict'] = config_dict
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


def build_config_dict(configs):
    """
    Build the config_dict needed for deployment to the provided service. Prompt the
    user for configs that are required but not provided and use the default configs
    from the operator to populate all the others.
    """
    if configs['config_path'] is not None:
        config_path = Path(configs["config_path"])

        if not config_path.exists():
            raise FileNotFoundError(
                "the config file {} is not found!".format(config_path)
            )

        config_dict = parse_config_file(config_path)
        # WARNING: this overides the name and operator with that provided via cli args
        configs.update(config_dict)
    else:
        no_config_file = True

    if configs['deployment_name'] is None:
        configs["deployment_name"] = input("Enter a Name for deployment: ")

    if configs['operator_name'] is not None:
        operator_name = configs["operator_name"]
    else:
        operator_name = choose_operator()
        configs["operator_name"] = operator_name

    operator_list = get_operator_list()
    operator = Operator(operator_list[operator_name])
    default_config = operator.deployment_config
    configs = fill_defaults(configs, default_config)

    return configs