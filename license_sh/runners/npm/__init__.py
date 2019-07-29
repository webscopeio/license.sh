import json
from os import path

from license_sh.reporters.ConsoleReporter import ConsoleReporter


class NpmRunner:
  """
  This class checks for dependencies in NPM projects and fetches license info
  for each of the packages (including transitive dependencies)
  """

  def __init__(self, directory: str, verbose: bool = True):
    self.directory = directory
    self.verbose = verbose
    self.package_json_path = path.join(directory, 'package.json')
    self.package_lock_path = path.join(directory, 'package-lock.json')

  @staticmethod
  def get_dependencies(package_name, all_dependencies, processed_dependencies):
    package_info = all_dependencies[package_name]
    direct_dependencies = package_info.get('requires', {}).keys()
    return {
      name: {
        "version": all_dependencies[name]['version'],
        "dependencies": NpmRunner.get_dependencies(name, all_dependencies, {})
      } for name in direct_dependencies
    }

  @staticmethod
  def transform_package_lock_to_dependency_tree(root_dependencies, all_dependencies):
    processed_dependencies = root_dependencies
    dependencies = {
      name: {
        'version': all_dependencies[name]['version'],
        'dependencies': NpmRunner.get_dependencies(name, all_dependencies, processed_dependencies),
      } for name in root_dependencies.keys()
    }
    return dependencies

  def check(self):
    if self.verbose:
      print("===========")
      print(f"Initiated License.sh check for NPM project {self.directory}")

    with open(self.package_json_path) as package_json_file:
      package_json = json.load(package_json_file)
      root_dependencies = package_json['dependencies']

    with open(self.package_lock_path) as package_lock_file:
      package_lock = json.load(package_lock_file)
      all_dependencies = package_lock['dependencies']

    dependencies = NpmRunner.transform_package_lock_to_dependency_tree(root_dependencies, all_dependencies)

    ConsoleReporter.output(dependencies, {})
    # for dependency, content in dependencies.items():
    #   result = subprocess.run(['npm', 'info', f'{dependency}@{content["version"]}', '--json'], stdout=subprocess.PIPE)
    #   print('\u2705', json.loads(result.stdout)['license'], f'{dependency}@{content["version"]}')
