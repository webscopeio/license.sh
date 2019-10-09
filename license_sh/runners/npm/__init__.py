import asyncio
import json
import subprocess
from os import path
from anytree import AnyNode, PreOrderIter
from typing import Dict

from yaspin import yaspin

def parse(json_element, parent = None) -> AnyNode:
  """Recursivelly parse `npm list --json --long` output to anytree
  
  Arguments:
      json_element {json} -- Json root element
  
  Keyword Arguments:
      parent {AnyNode} -- Parent of json_element (default: {None})
  
  Returns:
      AnyNode -- Parsed tree from json_element
  """
  if not json_element:
    return None
  name = json_element.get('name', 'project_name')
  version = json_element.get('version', 'project_version')
  node = AnyNode(name=name, version=version, parent=parent, license=license)
  for dependency in json_element.get('dependencies', {}).values():
    parse(dependency, node)
  return node

def parse_licenses(json_element, result = None) -> Dict[str, str]:
  """Recursivelly parse `npm list --json --long` output to license dict
  
  Arguments:
      json_element {json} -- Json root element
  
  Keyword Arguments:
      result {dict} -- dict that is updated (default: {None})
  
  Returns:
      Dict[str, str] -- Result dict with NAME@VERSION as key and license as value
  """
  if not json_element:
    return None
  if result is None:
    result = {}
  name = json_element.get('name', 'project_name')
  version = json_element.get('version', 'project_version')
  license = json_element.get('license', None)
  if not license:
    for license_data in json_element.get('licenses', []):
      if type(license_data) is dict:
        license_type = license_data.get('type', None)
        if not license:
          license = license_type
        else:
          license += ' AND ' + license_type
  if license is not None:
    result[f'{name}@{version}'] = license
  for dependency in json_element.get('dependencies', {}).values():
    parse_licenses(dependency, result)
  return result

class NpmRunner:
  """
  This class checks for dependencies in NPM projects and fetches license info
  for each of the packages (including transitive dependencies)
  """

  def __init__(self, directory: str):
    self.directory = directory
    self.verbose = True
    self.package_json_path = path.join(directory, 'package.json')

  def check(self):
    with open(self.package_json_path) as package_json_file:
      package_json = json.load(package_json_file)
      project_name = package_json.get('name', 'package.json')

    if self.verbose:
      print("===========")
      print(f"Initiated License.sh check for NPM project {project_name} located at {self.directory}")
      print("===========")
      

    with yaspin(text="Analysing dependencies ...") as sp:
      result = subprocess.run(['npm', 'list', '--json', '--long', '--prefix', self.directory], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      json_data = json.loads(result.stdout)
      dep_tree = parse(json_data)
      license_map = parse_licenses(json_data)

    for node in PreOrderIter(dep_tree):
      node.license = license_map.get(f'{node.name}@{node.version}', None)

    return dep_tree, license_map
