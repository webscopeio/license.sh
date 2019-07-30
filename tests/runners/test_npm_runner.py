import unittest

from license_sh.runners.npm import NpmRunner


class NpmRunnerTestCase(unittest.TestCase):

  def test__get_dependencies__basic_version(self):
    all_dependencies = {
      "dependency-1": {
        "version": "3.3.3",
      },
      "dependency-2": {
        "version": "3.3.3",
      },
      "dependency-3": {
        "version": "3.3.3",
        "requires": {
          "dependency-1": "^3.0.0 || ^4.0.0"
        }
      },
    }
    dep3_dependencies = NpmRunner.get_dependencies("dependency-3", all_dependencies)
    self.assertDictEqual(dep3_dependencies, {
      "dependency-1": {
        "version": "3.3.3",
        "dependencies": {},
      },
    })

  def test__get_dependencies__nested_version(self):
    all_dependencies = {
      "dependency-1": {
        "version": "3.3.3",
        "requires": {
          "dependency-2": "3.3.3"
        }
      },
      "dependency-2": {
        "version": "3.3.3",
      },
      "dependency-3": {
        "version": "3.3.3",
        "requires": {
          "dependency-1": "^3.0.0 || ^4.0.0"
        }
      },
    }
    dep3_dependencies = NpmRunner.get_dependencies("dependency-3", all_dependencies)
    self.assertDictEqual(dep3_dependencies, {
      "dependency-1": {
        "version": "3.3.3",
        "dependencies": {
          "dependency-2": {
            "version": "3.3.3",
            "dependencies": {},
          }
        }
      },
    }, )

  def test__get_dependencies__bundled_dependency(self):
    all_dependencies = {
      "dependency-3": {
        "version": "3.3.3",
        "requires": {
          "dependency-1": "^3.0.0 || ^4.0.0"
        },
        "dependencies": {
          "dependency-1": {
            "version": "3.0.0",
            "bundled": "true",
          }
        }
      },
    }
    dep3_dependencies = NpmRunner.get_dependencies("dependency-3", all_dependencies)
    self.assertDictEqual(dep3_dependencies, {
      "dependency-1": {
        "version": "3.3.3",
        "dependencies": {}
      },
    }, )

  @unittest.skip
  def test__get_dependencies__for_recursive_dependencies(self):
    all_dependencies = {
      "dependency-3": {
        "version": "3.3.3",
        "requires": {
          "dependency-1": "3.0.0"
        },
      },
      "dependency-1": {
        "version": "3.0.0",
        "requires": {
          "dependency-3": "3.3.3"
        },
      },
    }
    dep3_dependencies = NpmRunner.get_dependencies("dependency-3", all_dependencies)
    self.assertDictEqual(dep3_dependencies, {
      "dependency-1": {
        "version": "3.0.0",
        "dependencies": {
          "dependency-3": "recursive",
        }
      }
    })


if __name__ == '__main__':
  unittest.main()
