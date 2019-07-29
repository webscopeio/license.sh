from pprint import pprint


class ConsoleReporter:
  @staticmethod
  def output(dependency_tree, license_map):
    pprint(dependency_tree)
