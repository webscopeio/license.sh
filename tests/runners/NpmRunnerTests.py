import unittest

from license_sh.runners.npm import NpmRunner


class NpmRunnerTestCase(unittest.TestCase):
  @unittest.skip
  def test__package_lock_dependencies__resolved_to__license_sh_dependency_tree(self):
    dependencies = {
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

    root_dependencies = {
      "dependency-3": "3.3.3",
      "dependency-2": "3.3.3",
    }

    dependency_tree = NpmRunner.transform_package_lock_to_dependency_tree(root_dependencies, dependencies)
    self.assertDictEqual(dependency_tree, {
      "dependency-3": {
        "version": "3.3.3",
        "dependencies": {
          "dependency-1": {
            "version": "3.3.3",
          },
        },
      },
      "dependency-2": {
        "version": "3.3.3",
      }
    })

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
    dep3_dependencies = NpmRunner.get_dependencies("dependency-3", all_dependencies, {})
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
    dep3_dependencies = NpmRunner.get_dependencies("dependency-3", all_dependencies, {})
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


if __name__ == '__main__':
  unittest.main()
