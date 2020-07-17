import json
import sys
from os import path
from typing import List, Dict

from .project_identifier import ProjectType
from .types.configuration import ConfigurationType, LicenseWhitelist

DEFAULT_CONFIG_NAME = ".license-sh.json"
IGNORED_PACKAGES = "ignored_packages"
WHITELIST = "whitelist"


def get_config_path(path_to_config: str) -> str:
    return (
        path_to_config
        if path.isfile(path_to_config)
        else path.join(path_to_config, DEFAULT_CONFIG_NAME)
    )


def get_raw_config(path_to_config: str) -> Dict:
    config_path = get_config_path(path_to_config)
    try:
        with open(config_path) as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Config file '{config_path}' not found...", file=sys.stderr)
        return {}


def get_config(path_to_config: str) -> ConfigurationType:
    raw_config = get_raw_config(path_to_config)

    return (
        raw_config.get(WHITELIST, []),
        raw_config.get(IGNORED_PACKAGES, {}),
    )


def write_config(path_to_config: str, config):
    config_path = get_config_path(path_to_config)
    try:
        with open(config_path, "w+") as outfile:
            json.dump(config, outfile, indent=2, sort_keys=True)
            return True
    except FileNotFoundError:
        return False


def whitelist_licenses(path_to_config: str, licenses: List[str]):
    config = get_raw_config(path_to_config)
    current_whitelist: LicenseWhitelist = config.get(WHITELIST, [])
    config[WHITELIST] = list(set(current_whitelist + licenses))
    write_config(path_to_config, config)


def ignore_packages(path_to_config: str, project_type: ProjectType, packages: List[str]):
    config = get_raw_config(path_to_config)
    lang_ignored_packages = config.get(IGNORED_PACKAGES, {}).get(project_type.value, [])
    config.setdefault(IGNORED_PACKAGES, {}).setdefault(project_type.value, list(set(lang_ignored_packages + packages)))
    write_config(path_to_config, config)
