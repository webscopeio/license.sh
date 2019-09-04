from typing import Tuple

from anytree import Node, RenderTree, AnyNode, ContStyle, LevelOrderIter

from license_sh.helpers import GREEN, RESET, RED


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


def render_tree(tree: AnyNode, license_map, whitelist) -> None:
  for pre, fill, node in RenderTree(tree, style=ContStyle()):
    license = license_map.get(f'{node.name}@{node.version}', None)
    if node.is_root:
      print(' ')
    else:
      color = GREEN if license in whitelist else RED
      print(f"{pre}{node.name} - {node.version} - {color}{license}{RESET}")


class ConsoleReporter:
  @staticmethod
  def output(dependency_tree, flat_dependencies, license_map, whitelist, project_name=None, tree=False):
    for node in LevelOrderIter(dependency_tree):
      node.children = filter(lambda subnode: subnode.subtree_problem or subnode.license_problem, node.children)

    render_tree(dependency_tree, license_map, whitelist)
