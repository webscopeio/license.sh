import json
import os
from typing import List


def get_config(config_dir: str):
    config_path = os.path.join(config_dir, ".license-sh.json")
    try:
        with open(config_path) as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def write_config(config_dir: str, config):
    config_path = os.path.join(config_dir, ".license-sh.json")
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
