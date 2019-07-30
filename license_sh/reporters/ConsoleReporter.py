from anytree import Node, RenderTree
from license_sh.helpers import GREEN, RESET


def assign_children(parent, package):
  """
  Walk through the dependency tree and creates a Tree
  """
  for name, package in package.get('dependencies', {}).items():
    node = Node(name, parent=parent)
    assign_children(node, package)


class ConsoleReporter:
  @staticmethod
  def output(dependency_tree, license_map, project_name=None):
    root = Node(project_name or 'package.json')
    for name, package in dependency_tree.items():
      node = Node(name, parent=root)
      assign_children(node, package)

    for pre, fill, node in RenderTree(root):
      if node == root:
        print("%s%s%s" % ('npm 📦 ', pre, node.name,))
      else:
        print("%s%s%s" % (pre, node.name, ConsoleReporter.get_license_for(license_map, node.name)))

    print(f"\n{GREEN}All licenses are compatible with your .license-sh.json 🎉{RESET}\n")
    return 0

  @staticmethod
  def get_license_for(license_map, dependency: str):
    return f" {GREEN}\u2713 {license_map.get(dependency, 'Unknown')}{RESET}"
