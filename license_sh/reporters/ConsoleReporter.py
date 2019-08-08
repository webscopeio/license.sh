from anytree import Node, RenderTree, AsciiStyle
from license_sh.helpers import GREEN, RESET


def assign_children(parent, package):
  """
  Walk through the dependency tree and creates a Tree
  """
  for name, package in package.get('dependencies', {}).items():
    node = Node(f'{name}@{package.get("version")}', parent=parent)
    assign_children(node, package)


class ConsoleReporter:
  @staticmethod
  def output(dependency_tree, flat_dependencies, license_map, project_name=None):
    print(f'npm 📦 {project_name}')
    for pre, fill, node in RenderTree(dependency_tree, style=AsciiStyle()):
      license = license_map.get(f'{node.name}@{node.version}', None)
      print(f"{pre}{node.name} - {node.version} - {GREEN}{license}{RESET}")

    print(f"\n✅ {GREEN}All licenses are compatible with your .license-sh.json 🎉{RESET}\n")
    return 0

  @staticmethod
  def get_license_for(license_map, dependency: str):
    return f" {GREEN}\u2713 {license_map.get(dependency, 'Unknown')}{RESET}"
