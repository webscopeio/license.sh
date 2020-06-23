import subprocess
import os
import json
from license_sh.analyze.analyze_shared import (
    add_analyze_to_dep_tree,
    get_node_analyze_dict,
)
from anytree import AnyNode
from typing import Dict, List


def get_analyze_npm_data(directory: str) -> Dict:
    """Analyze npm dependencies

  Args:
      directory (str): Path to the project

  Returns:
      [Dict]: Analyzed data as dictionary
  """
    subprocess.run(
        ["npm", "ci", "--silent", "--prefix", directory],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return get_node_analyze_dict(directory)


def analyze_npm(directory: str, dep_tree: AnyNode) -> AnyNode:
    """Run npm analyze

  Args:
      directory (str): Path to the project
      dep_tree (AnyNode): Dependency tree to update

  Returns:
      [AnyNode]: Updated tree with analyze
  """
    analyze_data = get_analyze_npm_data(directory)
    return add_analyze_to_dep_tree(analyze_data, dep_tree)
