import json
from os import path
from typing import List
from .project_identifier import ProjectType

DEFAULT_CONFIG_NAME = ".license-sh.json"
IGNORED_PACKAGES = "ignored_packages"
WHITELIST = "whitelist"

def get_ignored_packages(ignored_packages: dict):
    ignored_packages_map = {
            e.value: [] for e in ProjectType
        }
    if not ignored_packages:
        return ignored_packages_map
    project_list = [e.value for e in ProjectType]
    for project_type, ignored_packages in ignored_packages.items():
        if not project_type in project_list:
            print(f"Ignored packages for project '{project_type}' is not supported. Ignoring...")
            continue
        if not isinstance(ignored_packages, list):
            print(f"Ignored packages for project '{project_type}' are incorect. Ignoring...")
            ignored_packages_map[project_type] = []
            continue
        
        for ignored_package in ignored_packages:
            if not isinstance(ignored_package, str):
                print(f"Ignored package for project {project_type}, '{ignored_package}' is incorect. Ignoring...")
            else:
                ignored_packages_map[project_type].append(ignored_package)
    return ignored_packages_map


def get_config_path(path_to_config: str):
    return (
        path_to_config
        if path.isfile(path_to_config)
        else path.join(path_to_config, DEFAULT_CONFIG_NAME)
    )


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
