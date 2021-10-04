from .deployer_mng import load_deployer
from .config_mng import load_json_config

from rich.pretty import pprint


def deploy_bundle(bento_bundle, name, config, deployer):
    config_json = load_json_config(config_path=config)
    deployer = load_deployer(deployer)
    deployer.deploy(bento_bundle, name, config_json)


def update_deployment(bento_bundle, name, config, deployer):
    config_json = load_json_config(config_path=config)
    deployer = load_deployer(deployer)
    deployer.update(bento_bundle, name, config_json)


def describe_deployment(name, config, deployer):
    config_json = load_json_config(config_path=config)
    deployer = load_deployer(deployer)
    info_json = deployer.describe(name, config_json)
    pprint(info_json)


def delete_deployment(name, config, deployer):
    config_json = load_json_config(config_path=config)
    deployer = load_deployer(deployer)
    deployer.delete(name, config_json)
