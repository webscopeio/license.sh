from typing import Tuple

from anytree import Node, RenderTree, AsciiStyle, findall, Walker, AnyNode, ContStyle
from license_sh.helpers import GREEN, RESET


def assign_children(parent, package):
  """
  Walk through the dependency tree and creates a Tree
  """
  for name, package in package.get('dependencies', {}).items():
    node = Node(f'{name}@{package.get("version")}', parent=parent)
    assign_children(node, package)


def is_bad_license(license_map, node, whitelist):
  license = license_map.get(f'{node.name}@{node.version}', None)
  return license not in whitelist


def get_tree_path(nodes: Tuple[AnyNode, ...]) -> AnyNode:
  root_node = AnyNode(name='', version='')
  last_node = root_node
  for node in nodes:
    last_node = AnyNode(name=node.name, version=node.version, parent=last_node)
  return root_node


def render_tree(tree: AnyNode, license_map) -> None:
  for pre, fill, node in RenderTree(tree, style=ContStyle()):
    license = license_map.get(f'{node.name}@{node.version}', None)
    if node.parent:
      print(f"{pre}{node.name} - {node.version} - {GREEN}{license}{RESET}")
    else:
      print(' ')


class ConsoleReporter:
  @staticmethod
  def output(dependency_tree, flat_dependencies, license_map, whitelist, project_name=None):
    bad_nodes = findall(dependency_tree, filter_=lambda node: is_bad_license(license_map, node, whitelist))
    for bad_node in bad_nodes:
      w = Walker()
      upwards, common, downwards = w.walk(dependency_tree, bad_node)
      tree = get_tree_path(downwards)
      render_tree(tree, license_map)

    return 0

  # @staticmethod
  # def get_license_for(license_map, dependency: str):
  #   return f" {GREEN}\u2713 {license_map.get(dependency, 'Unknown')}{RESET}"
