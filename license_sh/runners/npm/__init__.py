import json
import subprocess
from os import path
from pprint import pprint

from yaspin import yaspin

from license_sh.reporters.ConsoleReporter import ConsoleReporter


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
  def get_dependencies(package_name, all_dependencies, package=None):
    # if package is not provided, we get it from all_dependencies
    package = package or all_dependencies[package_name]
    direct_dependencies = package.get('requires', {}).keys()
    version = package.get('version')

    def get_json(name):
      return {
        "version": version,
        "dependencies": NpmRunner.get_dependencies(
          name,
          all_dependencies,
          package.get('dependencies', {}).get(name, None)
        )
      }

    return {
      name: get_json(name) for name in direct_dependencies
    }

  @staticmethod
  def transform_package_lock_to_dependency_tree(root_dependencies, all_dependencies):
    dependencies = {
      name: {
        'version': all_dependencies[name]['version'],
        'dependencies': NpmRunner.get_dependencies(name, all_dependencies, all_dependencies[name]),
      } for name in root_dependencies.keys()
    }
    return dependencies

  @staticmethod
  def fetch_licenses(all_dependencies):
    license_map = {}
    counter = 0
    dependencies_len = len(all_dependencies)

    with yaspin(text="Fetching license info from npm ...") as sp:
      for dependency, content in all_dependencies.items():
        exact_version = f'{dependency}@{content["version"]}'
        result = subprocess.run(['npm', 'info', exact_version, '--json'], stdout=subprocess.PIPE)
        license = json.loads(result.stdout)['license']

        counter += 1
        percent = counter / dependencies_len
        sp.text = f"{'%.2f' % percent}% - {dependency} ~ {license}"
        license_map[dependency] = license

    return license_map

  def check(self):
    with open(self.package_json_path) as package_json_file:
      package_json = json.load(package_json_file)
      project_name = package_json['name']
      root_dependencies = package_json['dependencies']

    with open(self.package_lock_path) as package_lock_file:
      package_lock = json.load(package_lock_file)
      all_dependencies = package_lock['dependencies']

    if self.verbose:
      print("===========")
      print(f"Initiated License.sh check for NPM project {project_name} located at {self.directory}")
      print("===========")

    dependencies = NpmRunner.transform_package_lock_to_dependency_tree(root_dependencies, all_dependencies)

    license_map = {}
    # license_map = NpmRunner.fetch_licenses(all_dependencies)
    #
    # print("\n")
    ConsoleReporter.output(dependencies, license_map, project_name=project_name)
