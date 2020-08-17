import os
import re
import subprocess
import tempfile
from typing import Dict, List

from anytree import AnyNode, PreOrderIter

from license_sh.analyze.analyze_shared import run_askalono, LICENSE_GLOB

SUFFIX = ".dist-info"


def get_analyze_pipenv_data(directory: str, tmp_dir: str) -> List:
    """
    Analyze pipenv dependencies

    Args:
      directory (str): Path to the project

    Returns:
      [Dict]: Analyzed data as dictionary
    """
    requirements_output = subprocess.run(
        ["pipenv", "lock", "-r"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=directory,
    ).stdout.decode("utf-8")
    requirements_path = os.path.join(tmp_dir, "requirements.txt")
    with open(requirements_path, "w") as requirements_file:
        requirements_file.write(requirements_output)

    subprocess.run(
        [
            "pipenv",
            "run",
            "pip",
            "install",
            "-r",
            requirements_path,
            "--target",
            tmp_dir,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=directory,
    )

    return run_askalono(tmp_dir)


def get_pipenv_analyze_dict(directory: str) -> Dict:
    """
    Get pipenv analyze dictionary

    Args:
        directory (str): Path to the project

    Returns:
        Dict: Dependency {name}-{version} as key, license text and analyzed license name and value
    """

    data_dict: Dict[str, List[Dict[str, str]]] = {}

    with tempfile.TemporaryDirectory() as dirpath:
        license_data = get_analyze_pipenv_data(directory, dirpath)
        for item in license_data:
            *path, folder_name, license_name = item.get("path").split("/")
            dep_id, *rest = folder_name.split(SUFFIX)
            if not data_dict.get(dep_id):
                data_dict[dep_id] = []
            with open(item.get("path"), "r") as license_file:
                license_text = license_file.read()
                license_result = item.get("result", {})
                data_dict[dep_id].append(
                    {
                        "data": license_text,
                        "name": license_result.get("license", {}).get("name"),
                        "file": license_name,
                    }
                )
        return data_dict


def add_analyze_to_dep_tree(analyze_dict: Dict, dep_tree: AnyNode):
    """Add analyze result to the nodes in the dependency tree

    Args:
      analyze_dict (Dict): Result of the pipenv analyze
      dep_tree (AnyNode): Dependency tree to update
    """
    for node in PreOrderIter(dep_tree):
        node_analyze_list = analyze_dict.get(f"{node.name}-{node.version}")
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


def analyze_pipenv(directory: str, dep_tree: AnyNode) -> AnyNode:
    """Run pipenv analyze

    Args:
      directory (str): Path to the project
      dep_tree (AnyNode): Dependency tree to update

    Returns:
      [AnyNode]: Updated tree with analyze
    """
    analyze_dict = get_pipenv_analyze_dict(directory)
    return add_analyze_to_dep_tree(analyze_dict, dep_tree)
