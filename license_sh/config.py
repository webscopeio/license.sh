import json
from os import path
from typing import List

DEFAULT_CONFIG_NAME = '.license-sh.json'

def get_config_path(path_to_config: str):
    return path_to_config if path.isfile(path_to_config) else path.join(path_to_config, DEFAULT_CONFIG_NAME) 

def get_config(path_to_config: str):
    config_path = get_config_path(path_to_config)
    try:
        with open(config_path) as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def write_config(path_to_config: str, config):
    config_path = get_config_path(path_to_config)
    try:
        with open(config_path, "w+") as outfile:
            json.dump(config, outfile, indent=2, sort_keys=True)
            return True
    except FileNotFoundError:
        return False


def whitelist_licenses(path_to_config: str, licenses: List[str]):
    config = get_config(path_to_config)
    config["whitelist"] = list(set(config.get("whitelist", []) + licenses))
    write_config(path_to_config, config)
