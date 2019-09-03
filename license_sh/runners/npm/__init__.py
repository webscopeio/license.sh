import asyncio
import json
from json import JSONDecodeError
from os import path

import aiohttp as aiohttp
import urllib3
from anytree import AnyNode

from license_sh.reporters.ConsoleReporter import ConsoleReporter

NPM_HOST = 'https://registry.npmjs.org'
http = urllib3.HTTPConnectionPool(NPM_HOST, num_pools=50)

from yaspin import yaspin


def flatten_package_lock_dependencies(package_lock_dependencies):
  """
  Flattens package.lock dependencies
  :param package_lock_dependencies:
  :return: tuple(flat_array, dep_mapping)
     WHERE
     array flat_array is a flat array of all dependencies
     dict dep_mapping is a tree representing nested dependencies
  """
  # get the root dependencies
  root_deps = [(name, dep.get('version')) for name, dep in package_lock_dependencies.items()]

  for dep in package_lock_dependencies.values():
    version, requires, dependencies = [dep.get(k, None) for k in ('version', 'requires', 'dependencies')]
    if dependencies:
      deps = flatten_package_lock_dependencies(dependencies)
      root_deps += deps

  return set(root_deps)


def add_nested_dependencies(dependency, package_lock_tree, parent):
  for name, version_request in dependency.get('requires', {}).items():
    node = AnyNode(name=name, version_request=version_request, parent=parent, dependencies=dependency.get('dependencies'))

    dep = None
    p = node
    names = []
    while p.parent:
      if dep is None and p.dependencies and p.dependencies.get(name):
        dep = p.dependencies.get(name)
      p = p.parent
      names.append(p.name)

    # check the root
    if dep is None and p.dependencies and p.dependencies.get(name):
      dep = p.dependencies.get(name)

    node.version = dep.get('version')

    names = names[:-1]  # let's forget about top level

    # if I'm not already in a tree
    if name not in names:
      if dep:
        add_nested_dependencies(dep, package_lock_tree, node)


def get_dependency_tree(package_json, package_lock_tree):
  root = AnyNode(name=package_json.get('name', 'package.json'), dependencies=package_lock_tree,
                 version=package_json.get('version'))

  # load root dependencies from package.json
  for dep_name in package_json.get('dependencies', {}).keys():
    dependency = package_lock_tree[dep_name]
    version = dependency.get("version")
    parent = AnyNode(name=dep_name, version=version, parent=root, dependencies=dependency.get('dependencies'))
    add_nested_dependencies(dependency, package_lock_tree, parent=parent)

  return root


class NpmRunner:
  """
  This class checks for dependencies in NPM projects and fetches license info
  for each of the packages (including transitive dependencies)
  """

  def __init__(self, directory: str, config):
    self.directory = directory
    self.verbose = True
    self.config = config
    self.package_json_path = path.join(directory, 'package.json')
    self.package_lock_path = path.join(directory, 'package-lock.json')

  @staticmethod
  def fetch_licenses(all_dependencies):
    license_map = {}

    urls = [f'{NPM_HOST}/{dependency}/{version}' for dependency, version in all_dependencies]

    with yaspin(text="Fetching license info from npm ...") as sp:
      async def fetch(session, url):
        async with session.get(url) as resp:
          return await resp.text()
          # Catch HTTP errors/exceptions here

      async def fetch_concurrent(urls):
        loop = asyncio.get_event_loop()
        async with aiohttp.ClientSession() as session:
          tasks = []
          for u in urls:
            tasks.append(loop.create_task(fetch(session, u)))

          for result in asyncio.as_completed(tasks):
            try:
              page = json.loads(await result)
              license_map[f"{page['name']}@{page['version']}"] = page.get('license', 'Unknown')
            except JSONDecodeError:
              # TODO - investiage why does such a thing happen
              pass

      asyncio.run(fetch_concurrent(urls))

    return license_map

  def check(self):
    with open(self.package_json_path) as package_json_file:
      package_json = json.load(package_json_file)
      project_name = package_json.get('name', 'package.json')

    with open(self.package_lock_path) as package_lock_file:
      package_lock = json.load(package_lock_file)
      all_dependencies = package_lock['dependencies']

    if self.verbose:
      print("===========")
      print(f"Initiated License.sh check for NPM project {project_name} located at {self.directory}")
      print("===========")

    with yaspin(text="Analysing dependencies ...") as sp:
      dep_tree = get_dependency_tree(package_json, all_dependencies)
      flat_dependencies = flatten_package_lock_dependencies(all_dependencies)
    license_map = NpmRunner.fetch_licenses(flat_dependencies)

    return dep_tree, license_map
