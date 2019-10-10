import json
import subprocess
import os
from os import path
from anytree import AnyNode, PreOrderIter, RenderTree
from typing import Dict, List
from yaspin import yaspin
from pathlib import Path

PARSE_YARN_LOCK_PATH = path.join(Path(__file__).parent, '..', '..', '..', 'js')
PARSE_YARN_LOCK_SCRIPT = path.join(PARSE_YARN_LOCK_PATH, 'parseYarnLock.js')

def parse_yarn_lock(json_element) -> Dict[str, str]:
  package_map = {}
  for (key, dependency) in json_element.get('object', {}).items():
    package_map[key] = dependency.get('version', None)
  return package_map

def get_name(name: str):
  parsedName, signName, *rest = name.split('@')
  if name.startswith('@'):
    return '@' + signName
  return parsedName

def get_flat_tree(dependencies: List, package_map: Dict[str, str]) -> Dict:
  flat_tree = {}
  for dependency in dependencies:
    dep_full_name = dependency.get('name')
    flat_tree[dependency.get('name')] = {
      'name': get_name(dep_full_name),
      'version': package_map.get(dep_full_name),
      'dependencies': get_flat_tree(dependency.get('children', []), package_map)
    }
  return flat_tree

def add_nested_dependencies(dependency, parent):
  for name, dependency in dependency.get('dependencies', {}).items():
    dep_name = dependency.get('name')
    dep_version = dependency.get('version')
    full_dep_name = f'{dep_name}@{dep_version}'
    dep_dependencies = dependency.get('dependencies', {})
    if not dep_version:
      continue
    node = AnyNode(name=dep_name, version=dependency.get('version'), parent=parent, dependencies=dep_dependencies)

    dep = None
    p = node
    names = []
    while p.parent:
      if not dep and p.dependencies and p.dependencies.get(full_dep_name) and p.dependencies.get(full_dep_name).get('dependencies'):
        node.dependencies = p.dependencies.get(full_dep_name).get('dependencies')
        dep = p.dependencies.get(full_dep_name)
      p = p.parent
      names.append(p.name)

    # check the root
    if not dep and p.dependencies and p.dependencies.get(full_dep_name) and p.dependencies.get(full_dep_name).get('dependencies'):
      node.dependencies = p.dependencies.get(full_dep_name).get('dependencies')
      dep = p.dependencies.get(full_dep_name)

    names = names[:-1]  # let's forget about top level
    # if I'm not already in a tree
    if dep_name not in names:
      if dep:
        add_nested_dependencies(dep, node)

def get_dependency_tree(flat_tree, package_json, package_map):
  root = AnyNode(name=package_json.get('name', 'package.json'), dependencies=flat_tree,
                 version=package_json.get('version'))
  # load root dependencies from package.json
  for dep_name, dep_version in package_json.get('dependencies', {}).items():
    resolved_version = package_map.get(f'{dep_name}@{dep_version}')
    full_dep_name = f'{dep_name}@{resolved_version}'
    dependency = flat_tree[full_dep_name]
    version = dependency.get('version')
    parent = AnyNode(name=dep_name, version=version, parent=root, dependencies=dependency.get('dependencies'))
    add_nested_dependencies(dependency, parent)

  return root

class YarnRunner:
  """
  This class checks for dependencies in Yarn projects and fetches license info
  for each of the packages (including transitive dependencies)
  """

  def __init__(self, directory: str):
    self.directory = directory
    self.verbose = True
    self.package_json_path = path.join(directory, 'package.json')
    self.yarn_lock_path = path.join(directory, 'yarn.lock')

  def check(self):
    with open(self.package_json_path) as package_json_file:
      package_json = json.load(package_json_file)
      project_name = package_json.get('name', 'project_name')

    if self.verbose:
      print("===========")
      print(f"Initiated License.sh check for YARN project {project_name} located at {self.directory}")
      print("===========")


    with yaspin(text="Analysing dependencies ...") as sp:
      tree_list_output = json.loads((subprocess.run([
        'yarn',
        'list',
        '--json',
        '--silent',
        '--no-progress',
        '--cwd',
        self.directory],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
      )).stdout)
      # install yarn lock parser
      subprocess.run([
        'yarn',
        'install',
        '--cwd',
        PARSE_YARN_LOCK_PATH]
      )
      # run yarn lock parser
      yarn_lock_output = json.loads(subprocess.run([
        'node',
        PARSE_YARN_LOCK_SCRIPT,
        f'{self.directory}/yarn.lock'],
        stdout=subprocess.PIPE
      ).stdout)
      package_map = parse_yarn_lock(yarn_lock_output)
      flat_tree = get_flat_tree(tree_list_output.get('data', {}).get('trees', []), package_map)
      dep_tree = get_dependency_tree(flat_tree, package_json, package_map)

      license_map = {} # TODO: Add license map
      
      
    for node in PreOrderIter(dep_tree):
      delattr(node, 'dependencies')
      # license_map[f'{node.name}@{node.version}'] = 'MIT' # TODO: Remove
      node.license = license_map.get(f'{node.name}@{node.version}', None)

    return dep_tree, license_map
