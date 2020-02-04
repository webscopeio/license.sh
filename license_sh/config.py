import json
from os import path
from typing import List

DEFAULT_CONFIG_NAME = '.license-sh.json'

def get_config(config_path: str):
    config = config_path if path.isfile(config_path) else path.join(config_path, DEFAULT_CONFIG_NAME)
    try:
        with open(config) as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def write_config(config_dir: str, config):
    config_path = path.join(config_dir, ".license-sh.json")
    try:
        with open(config_path, "w+") as outfile:
            json.dump(config, outfile, indent=2, sort_keys=True)
            return True
    except FileNotFoundError:
        return False


def whitelist_licenses(config_dir: str, licenses: List[str]):
    config = get_config(config_dir)
    config["whitelist"] = list(set(config.get("whitelist", []) + licenses))
    write_config(config_dir, config)
