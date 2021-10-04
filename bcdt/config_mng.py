import json


def load_json_config(config_path):
    with open(config_path, "r") as f:
        config_json = json.load(f)

    return config_json
