from importlib import resources
from license_sh.analyze import lib
from anytree import AnyNode, PreOrderIter
from typing import Dict, List
from ..helpers import get_node_id
import os
import re
import json
import subprocess
from sys import platform

GIT_IGNORE = ".gitignore"
GIT_IGNORE_DISABLED = ".gitignore_disabled"
PACKAGE_JSON = "package.json"
LICENSE_GLOB = "[lL][iI][cC][eE][nN][sScC][eE]*"
GLOB = f"{{{LICENSE_GLOB},[Rr][eE][aA][Dd][Mm][eE]*}}"
UNKNOWN = "unknown"

ASKALONO_BINARY = {
    "linux": "askalono.linux",
    "win32": "askalono.exe",
    "cygwin": "askalono.exe",
    "darwin": "askalono.osx",
}


def get_askalono():
    return ASKALONO_BINARY[platform]


def run_askalono(directory: str, glob: str = GLOB) -> List:
    """ Analyze node modules dependencies

  Args:
      directory (str): Path to the project

  Returns:
      [List]: Result of an node_modules crawling with analyze as List of Dictionaries
  """
    with resources.path(lib, get_askalono()) as askalono_path:
        result = []
        git_ignore_path = os.path.join(directory, GIT_IGNORE)
        git_ignore_path_disabled = os.path.join(directory, GIT_IGNORE_DISABLED)
        git_ignore_present = os.path.isfile(git_ignore_path)
        try:
            if git_ignore_present:
                os.rename(git_ignore_path, git_ignore_path_disabled)
            output_str = subprocess.run(
                [
                    askalono_path,
                    "--format",
                    "json",
                    "crawl",
                    "--glob",
                    glob,
                    directory,
                ],
                stdout=subprocess.PIPE,
            ).stdout.decode("utf-8")
            output_lines = output_str.split("\n")
            for line in output_lines:
                try:
                    result.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        finally:
            if git_ignore_present:
                os.rename(git_ignore_path_disabled, git_ignore_path)

        return result


def get_node_analyze_dict(directory: str) -> Dict:
    """ Get node_modules analyze with package json data

  Args:
      directory (str): Path to the project 

  Returns:
      [Dict]: Project id as a key and Dict with license text and analyzed license name
  """
    data_dict = {}
    license_data = run_askalono(directory)
    for item in license_data:
        path = os.path.join(*item.get("path").split("/")[0:-1])
        package_file = os.path.join(path, PACKAGE_JSON)
        if os.path.isfile(package_file):
            with open(package_file, "r") as package_file:
                package_json = json.load(package_file)
                node_id = get_node_id(
                    package_json.get("name", "project_name"),
                    package_json.get("version", "unknown"),
                )

            if not data_dict.get(node_id):
                data_dict[node_id] = []

            with open(item.get("path"), "r") as license_file:
                license_text = license_file.read()
                license_result = item.get("result", {})
                if license_text in [
                    item.get("data") for item in data_dict.get(node_id)
                ]:
                    continue
                data_dict[node_id].append(
                    {
                        "data": license_text,
                        "name": license_result.get("license", {}).get("name"),
                        "file": item.get("path").split("/")[-1],
                    }
                )
    return data_dict


def add_analyze_to_dep_tree(analyze_dict: Dict, dep_tree: AnyNode):
    """Add analyze result to the nodes in the dependency tree

  Args:
      analyze_dict (Dict): Result of the node_modules analyze
      dep_tree (AnyNode): Dependency tree to update
  """
    for node in PreOrderIter(dep_tree):
        node_analyze_list = analyze_dict.get(node.id)
        node.analyze = []
        if not node_analyze_list:
            continue
        for node_analyze in node_analyze_list:
            if re.match(LICENSE_GLOB, node_analyze.get("file", "")) or node_analyze.get(
                "name"
            ):
                node_analyze.pop("file", None)
                node.analyze.append(node_analyze)
    return dep_tree
