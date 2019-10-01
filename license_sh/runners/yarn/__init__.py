import json
import subprocess
from os import path
from anytree import AnyNode, PreOrderIter
from yaspin import yaspin

def get_name_and_version(name):
  split_name = name.split('@')
  if len(split_name) < 1:
    return name, None
  if name[0] is '@':
    dep_name = '@' + split_name[-2]
  else:
    dep_name = split_name[-2]
  return dep_name, split_name[-1]

def get_dependency_licenses(license_data):
  result = {}
  lisenses = license_data.get('data', {}).get('body', []) 
  for license in lisenses:
    result[f"{license[0]}@{license[1]}"] = license[2]
  return result

def add_nested_dependencies(dependency, yarn_lock_tree, parent):
  for child in dependency.get('children', []):
    dep_name, dep_version = get_name_and_version(child.get('name'))
    node = AnyNode(name=dep_name, version=dep_version, parent=parent, dependencies=child.get('children'))
    add_nested_dependencies(child, yarn_lock_tree, node)


def get_dependency_tree(package_json, yarn_lock_tree):
  root = AnyNode(name=package_json.get('name', 'package.json'), dependencies=yarn_lock_tree,
                 version=package_json.get('version'))

  for dependency in yarn_lock_tree.get('data', {}).get('trees', []):
    dep_name, dep_version = get_name_and_version(dependency.get('name'))
    parent = AnyNode(name=dep_name, version=dep_version, parent=root, dependencies=dependency.get('children', []))
    add_nested_dependencies(dependency, yarn_lock_tree, parent=parent)
  return root

def get_dependency_versions(yarn_lock):
  version_map = {}
  for name in yarn_lock.keys():
    version_map[name] = yarn_lock[name].get('version', None)
  return version_map


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
      project_name = package_json.get('name', 'package.json')    

    if self.verbose:
      print("===========")
      print(f"Initiated License.sh check for YARN project {project_name} located at {self.directory}")
      print("===========")


    with yaspin(text="Analysing dependencies ...") as sp:
      all_dependencies = json.loads((subprocess.run([
        'yarn',
        'list',
        '--json',
        '--no-progress',
        '--no-interactive',
        '--cwd',
        self.directory],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
      )).stdout)
      license_result = subprocess.run([
        'yarn',
        'licenses',
        'list',
        '--json',
        '--no-progress',
        '--no-interactive',
        '--cwd',
        self.directory],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
      ).stdout
      yarn_lock_result = json.loads(subprocess.run([
        'node',
        './js/lockToJson.js',
        f'{self.directory}/yarn.lock'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
      ).stdout).get('object', {})
      
      
      dep_tree = get_dependency_tree(package_json, all_dependencies)
      for line in license_result.split('\n'):
        if '{"type":"table"' in line:
          license_map = get_dependency_licenses(json.loads(line))
      version_map = get_dependency_versions(yarn_lock_result)
      
      for node in PreOrderIter(dep_tree):
        delattr(node, 'dependencies')
        node.version = version_map.get(f'{node.name}@{node.version}', node.version)
        node.license = license_map.get(f'{node.name}@{node.version}', None)

    return dep_tree, license_map
