import subprocess
import os
import json
from license_sh.analyze.analyze_shared import (
    add_analyze_to_dep_tree,
    get_node_analyze_dict,
)
from anytree import AnyNode


def get_analyze_yarn_data(directory: str):
    """Analyze yarn dependencies

  Args:
      directory (str): Path to the project

  Returns:
      [Dict]: Analyzed data as dictionary
  """
    subprocess.run(
        ["yarn", "install", "--pure-lockfile", "--cwd", directory],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return get_node_analyze_dict(directory)


def analyze_yarn(directory: str, dep_tree: AnyNode):
    """Run yarn analyze

  Args:
      directory (str): Path to the project
      dep_tree (AnyNode): Dependency tree to update

  Returns:
      [AnyNode]: Updated tree with analyze
  """
    analyze_data = get_analyze_yarn_data(directory)
    return add_analyze_to_dep_tree(analyze_data, dep_tree)
