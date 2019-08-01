import unittest

from anytree import AnyNode, RenderTree
from anytree.exporter import DictExporter

from license_sh.runners.npm import flatten_package_lock_dependencies, get_dependency_tree


class NpmRunnerTestCase(unittest.TestCase):
  PACKAGE_LOCK_DEPENDENCIES = {
    "@company/package1": {
      "version": "1.1.1",
      "resolved": "...",
      "requires": {
        "package2": "^2.2.2",
        "package3": "^3.3.3",
        "package4": "4.4.4",
        "package5": "5.5.5",
      },
      "dependencies": {
        "package2": {
          "version": "2.2.2",
          "resolved": "...",
          "integrity": "...",
          "requires": {
            "package5": "^5.5.5",
            "package7": "7.7.7",
          },
          "dependencies": {
            "package7": {
              "version": "7.7.7",
            }
          }
        },
        "package3": {
          "version": "3.3.3",
          "requires": {
            "package7": "7.7.6",
          },
          "dependencies": {
            "package7": {
              "version": "7.7.6",
            }
          }
        },
        "package5": {
          "version": "5.5.5",
          "requires": {
            "package6": "6.6.6",
          },
          "dependencies": {
            "package6": {
              "version": "6.6.6",
            }
          }
        }
      }
    },
    "package5": {
      "version": "5.5.5",
      "requires": {
        "package6": "6.6.6",
      },
      "dependencies": {
        "package6": {
          "version": "6.6.6",
        }
      }
    },
    "package4": {
      "version": "4.4.4",
      "requires": {
        "package6": "6.6.6",
      },
      "dependencies": {
        "package6": {
          "version": "6.6.6",
        }
      }
    }
  }

  PACKAGE_JSON = {
    "name": "Name",
    "version": "0.0.1",
    "dependencies": {
      "@company/package1": "1.1.1",
      "package4": "4.4.4",
    }
  }

  def test_package_lock_format__flatten_fn_is_called__package_lock_is_flattened(self):
    flat_deps = flatten_package_lock_dependencies(self.PACKAGE_LOCK_DEPENDENCIES)
    self.assertSetEqual(flat_deps, {
      ("@company/package1", "^1.1.1"),
      ("package2", "2.2.2"),
      ("package3", "3.3.3"),
      ("package4", "4.4.4"),
      ("package5", "5.5.5"),
      ("package6", "6.6.6"),
      ("package7", "7.7.6"),
      ("package7", "7.7.7"),
    })

  def test_get_dependency_tree(self):
    tree = get_dependency_tree(self.PACKAGE_JSON, self.PACKAGE_LOCK_DEPENDENCIES)
    exporter = DictExporter()
    expected = AnyNode(name='Name')
    # first level
    package1 = AnyNode(name='@company/package1', parent=expected, version="1.1.1")
    package4 = AnyNode(name='package4', parent=expected, version="4.4.4")

    package2 = AnyNode(name='package2', parent=package1, version="2.2.2")
    AnyNode(name='package5', parent=package2, version="5.5.5")
    AnyNode(name='package7', parent=package2, version="7.7.7")

    package3 = AnyNode(name='package3', parent=package1, version="3.3.3")
    AnyNode(name='package7', parent=package3, version="7.7.6")

    AnyNode(name='package4', parent=package1, version="4.4.4")

    package5 = AnyNode(name='package5', parent=package1, version="5.5.5")
    AnyNode(name='package6', parent=package5, version="6.6.6")

    AnyNode(name='package6', parent=package4, version="6.6.6")

    print(RenderTree(expected))
    self.assertDictEqual(exporter.export(tree), exporter.export(expected))



if __name__ == '__main__':
  unittest.main()
