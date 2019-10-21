import unittest
import json

from license_sh.runners.yarn import (
    parse_yarn_lock,
    get_name,
    get_flat_tree,
    get_dependency_tree,
)


class ConsoleReporterTestCase(unittest.TestCase):
    def test_get_name_simple(self):
        name = get_name("test@1.2.3")
        self.assertEqual(name, "test")

    def test_get_name_simple_caret(self):
        name = get_name("test@^1.2.3")
        self.assertEqual(name, "test")

    def test_get_sign_name(self):
        name = get_name("@test@^1.2.3")
        self.assertEqual(name, "@test")

    def test_empty_lock(self):
        lock_file = """{
  "type": "success",
  "object": {}
}
"""
        package_map = parse_yarn_lock(json.loads(lock_file))
        self.assertFalse(package_map)

    def test_single_child_lock(self):
        lock_file = """{
  "type": "success",
  "object": {
    "toolbox-core@^1.0.1": {
      "version": "1.1.1"
    }
  }
}
"""
        package_map = parse_yarn_lock(json.loads(lock_file))
        self.assertEqual(package_map.get("toolbox-core@^1.0.1"), "1.1.1")

    def test_sign_child_lock(self):
        lock_file = """{
  "type": "success",
  "object": {
    "@toolbox-core@^1.0.1": {
      "version": "1.1.1"
    }
  }
}
"""
        package_map = parse_yarn_lock(json.loads(lock_file))
        self.assertEqual(package_map.get("@toolbox-core@^1.0.1"), "1.1.1")

    def test_multiple_children_lock(self):
        lock_file = """{
  "type": "success",
  "object": {
    "toolbox-core@^1.0.1": {
      "version": "1.1.1"
    },
    "toolbox-core1@^1.0.1": {
      "version": "1.1.2"
    },
    "toolbox-core2@^1.0.1": {
      "version": "1.1.3"
    }
  }
}
"""
        package_map = parse_yarn_lock(json.loads(lock_file))
        self.assertEqual(package_map.get("toolbox-core@^1.0.1"), "1.1.1")
        self.assertEqual(package_map.get("toolbox-core1@^1.0.1"), "1.1.2")
        self.assertEqual(package_map.get("toolbox-core2@^1.0.1"), "1.1.3")

    def test_single_child_flat_tree(self):
        tree_data = [{"name": "@babel/helper-create-class-features-plugin@^7.5.5"}]
        package_map = {"@babel/helper-create-class-features-plugin@^7.5.5": "1.1.3"}
        tree = get_flat_tree(tree_data, package_map)
        elem = tree.get("@babel/helper-create-class-features-plugin@^7.5.5")
        self.assertEqual(elem.get("name"), "@babel/helper-create-class-features-plugin")
        self.assertEqual(elem.get("version"), "1.1.3")

    def test_nested_children_flat_tree(self):
        tree_data = [
            {
                "name": "@babel/helper-create-class-features-plugin@^7.5.5",
                "children": [
                    {"name": "@babel/helper-plugin-utils@^7.0.0"},
                    {"name": "@babel/plugin-syntax-object-rest-spread@^7.2.0"},
                ],
            }
        ]
        package_map = {
            "@babel/helper-create-class-features-plugin@^7.5.5": "1.1.3",
            "@babel/helper-plugin-utils@^7.0.0": "9.9.9",
            "@babel/plugin-syntax-object-rest-spread@^7.2.0": "1.5.6",
        }
        tree = get_flat_tree(tree_data, package_map)
        elem = (
            tree.get("@babel/helper-create-class-features-plugin@^7.5.5")
            .get("dependencies")
            .get("@babel/plugin-syntax-object-rest-spread@^7.2.0")
        )
        self.assertEqual(elem.get("name"), "@babel/plugin-syntax-object-rest-spread")
        self.assertEqual(elem.get("version"), "1.5.6")

    def test_children_with_nested_child_flat_tree(self):
        tree_data = [
            {
                "name": "@babel/helper-create-class-features-plugin@^7.5.5",
                "children": [
                    {"name": "@babel/helper-plugin-utils@^7.0.0"},
                    {"name": "@babel/plugin-syntax-object-rest-spread@^7.2.0"},
                ],
            },
            {
                "name": "class-features-plugin@^7.5.5",
                "children": [{"name": "utils@^7.0.0"}],
            },
        ]
        package_map = {
            "@babel/helper-create-class-features-plugin@^7.5.5": "1.1.3",
            "@babel/helper-plugin-utils@^7.0.0": "9.9.9",
            "@babel/plugin-syntax-object-rest-spread@^7.2.0": "1.5.6",
            "class-features-plugin@^7.5.5": "8.5.3",
            "utils@^7.0.0": "6.5.2",
        }
        tree = get_flat_tree(tree_data, package_map)
        elem = (
            tree.get("@babel/helper-create-class-features-plugin@^7.5.5")
            .get("dependencies")
            .get("@babel/plugin-syntax-object-rest-spread@^7.2.0")
        )
        self.assertEqual(elem.get("name"), "@babel/plugin-syntax-object-rest-spread")
        self.assertEqual(elem.get("version"), "1.5.6")

        elem2 = (
            tree.get("class-features-plugin@^7.5.5")
            .get("dependencies")
            .get("utils@^7.0.0")
        )
        self.assertEqual(elem2.get("name"), "utils")
        self.assertEqual(elem2.get("version"), "6.5.2")

    def test_empty_dep_tree(self):
        package_json = {"name": "license", "version": "7.8.8", "dependencies": {}}
        tree_data = {}

        tree = get_dependency_tree(tree_data, package_json, {})
        self.assertEqual(tree.name, "license")
        self.assertEqual(tree.version, "7.8.8")

    def test_simple_dep_tree(self):
        package_json = {
            "name": "license",
            "version": "7.8.8",
            "dependencies": {"@babel/helper-create-class-features-plugin": "7.5.5"},
        }
        tree_data = {
            "@babel/helper-create-class-features-plugin@7.5.5": {
                "name": "@babel/helper-create-class-features-plugin",
                "version": "7.5.5",
                "dependencies": {
                    "@babel/helper-plugin-utils@7.0.0": {
                        "name": "@babel/helper-plugin-utils",
                        "version": "7.0.0",
                        "dependencies": {
                            "plugin-utils@7.0.0": {
                                "name": "plugin-utils",
                                "version": "7.0.0",
                            }
                        },
                    }
                },
            }
        }

        package_map = {
            "@babel/helper-create-class-features-plugin@7.5.5": "7.5.5",
            "@babel/helper-plugin-utils@7.0.0": "7.0.0",
            "plugin-utils@7.0.0": "7.0.0",
        }
        tree = get_dependency_tree(tree_data, package_json, package_map)
        self.assertEqual(
            tree.children[0].name, "@babel/helper-create-class-features-plugin"
        )
        self.assertEqual(tree.children[0].version, "7.5.5")
        self.assertEqual(
            tree.children[0].children[0].name, "@babel/helper-plugin-utils"
        )
        self.assertEqual(tree.children[0].children[0].version, "7.0.0")
        self.assertEqual(tree.children[0].children[0].children[0].name, "plugin-utils")
        self.assertEqual(tree.children[0].children[0].children[0].version, "7.0.0")

    def test_multiple_main_dep_tree(self):
        package_json = {
            "name": "license",
            "version": "7.8.8",
            "dependencies": {
                "@babel/helper-create-class-features-plugin": "7.5.5",
                "plugin": "7.5.0",
                "@license/plugin": "0.5.5",
            },
        }
        tree_data = {
            "@babel/helper-create-class-features-plugin@7.5.5": {
                "name": "@babel/helper-create-class-features-plugin",
                "version": "1.2.3",
                "dependencies": {},
            },
            "plugin@7.5.0": {"name": "plugin", "version": "1.2.3", "dependencies": {}},
            "@license/plugin@0.5.5": {
                "name": "plugin",
                "version": "0.5.5",
                "dependencies": {},
            },
        }

        package_map = {
            "@babel/helper-create-class-features-plugin@7.5.5": "7.5.5",
            "@license/plugin@0.5.5": "0.5.5",
            "plugin@7.5.0": "7.5.0",
        }
        tree = get_dependency_tree(tree_data, package_json, package_map)
        self.assertEqual(len(tree.children), 3)
        self.assertEqual(
            tree.children[0].name, "@babel/helper-create-class-features-plugin"
        )
        self.assertEqual(tree.children[0].version, "1.2.3")
        self.assertEqual(tree.children[1].name, "plugin")
        self.assertEqual(tree.children[1].version, "1.2.3")
        self.assertEqual(tree.children[2].name, "@license/plugin")
        self.assertEqual(tree.children[2].version, "0.5.5")

    def test_shared_dep_tree(self):
        package_json = {
            "name": "license",
            "version": "7.8.8",
            "dependencies": {
                "@babel/helper-create-class-features-plugin": "7.5.5",
                "plugin": "7.5.0",
            },
        }
        tree_data = {
            "@babel/helper-create-class-features-plugin@7.5.5": {
                "name": "@babel/helper-create-class-features-plugin",
                "version": "1.2.3",
                "dependencies": {
                    "@license/plugin@0.5.5": {
                        "name": "@license/plugin",
                        "version": "0.5.5",
                        "dependencies": {
                            "shared@0.5.5": {
                                "name": "shared",
                                "version": "0.5.5",
                                "dependencies": {},
                            }
                        },
                    }
                },
            },
            "plugin@7.5.0": {
                "name": "plugin",
                "version": "1.2.3",
                "dependencies": {
                    "shared@0.5.5": {
                        "name": "shared",
                        "version": "0.5.5",
                        "dependencies": {},
                    }
                },
            },
            "shared@0.5.5": {
                "name": "shared",
                "version": "0.5.5",
                "dependencies": {
                    "shared_child@0.5.5": {
                        "name": "shared_child",
                        "version": "0.5.5",
                        "dependencies": {},
                    }
                },
            },
        }
        package_map = {
            "@babel/helper-create-class-features-plugin@7.5.5": "7.5.5",
            "@license/plugin@0.5.5": "0.5.5",
            "shared_child@0.5.5": "0.5.5",
            "plugin@7.5.0": "7.5.0",
            "shared@0.5.5": "0.5.5",
        }
        tree = get_dependency_tree(tree_data, package_json, package_map)
        self.assertEqual(len(tree.children), 2)
        self.assertEqual(
            tree.children[0].name, "@babel/helper-create-class-features-plugin"
        )
        self.assertEqual(tree.children[0].version, "1.2.3")
        self.assertEqual(tree.children[0].children[0].name, "@license/plugin")
        self.assertEqual(tree.children[0].children[0].version, "0.5.5")
        self.assertEqual(tree.children[0].children[0].children[0].name, "shared")
        self.assertEqual(tree.children[0].children[0].children[0].version, "0.5.5")
        self.assertEqual(
            tree.children[0].children[0].children[0].children[0].name, "shared_child"
        )
        self.assertEqual(
            tree.children[0].children[0].children[0].children[0].version, "0.5.5"
        )
        self.assertEqual(tree.children[1].name, "plugin")
        self.assertEqual(tree.children[1].version, "1.2.3")
        self.assertEqual(tree.children[1].children[0].name, "shared")
        self.assertEqual(tree.children[1].children[0].version, "0.5.5")
        self.assertEqual(tree.children[1].children[0].children[0].name, "shared_child")
        self.assertEqual(tree.children[1].children[0].children[0].version, "0.5.5")

    def test_simple_optional_dep_tree(self):
        package_json = {
            "name": "license",
            "version": "7.8.8",
            "dependencies": {"@babel/helper-create-class-features-plugin": "^7.5.5"},
        }
        tree_data = {
            "@babel/helper-create-class-features-plugin@7.5.5": {
                "name": "@babel/helper-create-class-features-plugin",
                "version": "7.5.5",
            }
        }
        package_map = {"@babel/helper-create-class-features-plugin@^7.5.5": "7.5.5"}
        tree = get_dependency_tree(tree_data, package_json, package_map)
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(
            tree.children[0].name, "@babel/helper-create-class-features-plugin"
        )
        self.assertEqual(tree.children[0].version, "7.5.5")

    def test_circular_dep_tree(self):
        package_json = {
            "name": "license",
            "version": "7.8.8",
            "dependencies": {"@babel/helper-create-class-features-plugin": "7.5.5"},
        }
        tree_data = {
            "@babel/helper-create-class-features-plugin@7.5.5": {
                "name": "@babel/helper-create-class-features-plugin",
                "version": "7.5.5",
                "dependencies": {
                    "features-plugin@7.5.5": {
                        "name": "features-plugin",
                        "version": "7.5.5",
                    }
                },
            },
            "features-plugin@7.5.5": {
                "name": "features-plugin",
                "version": "7.5.5",
                "dependencies": {
                    "@babel/helper-create-class-features-plugin@7.5.5": {
                        "name": "@babel/helper-create-class-features-plugin",
                        "version": "7.5.5",
                    }
                },
            },
        }
        package_map = {"@babel/helper-create-class-features-plugin@7.5.5": "7.5.5"}
        tree = get_dependency_tree(tree_data, package_json, package_map)
        self.assertEqual(
            tree.children[0].name, "@babel/helper-create-class-features-plugin"
        )
        self.assertEqual(tree.children[0].version, "7.5.5")
        self.assertEqual(tree.children[0].children[0].name, "features-plugin")
        self.assertEqual(tree.children[0].children[0].version, "7.5.5")
        self.assertEqual(
            tree.children[0].children[0].children[0].name,
            "@babel/helper-create-class-features-plugin",
        )
        self.assertEqual(tree.children[0].children[0].children[0].version, "7.5.5")
        self.assertEqual(len(tree.children[0].children[0].children[0].children), 0)

    def test_same_nested_dep_tree(self):
        package_json = {
            "name": "license",
            "version": "7.8.8",
            "dependencies": {"@babel/helper-create-class-features-plugin": "7.5.5"},
        }
        tree_data = {
            "@babel/helper-create-class-features-plugin@7.5.5": {
                "name": "@babel/helper-create-class-features-plugin",
                "version": "7.5.5",
                "dependencies": {
                    "features-plugin@^7.5.5": {
                        "name": "features-plugin",
                        "version": "7.5.5",
                    },
                    "features-plugin@7.5.5": {
                        "name": "features-plugin",
                        "version": None,
                        "dependencies": {
                            "@babel/plugin@7.5.5": {
                                "name": "@babel/plugin",
                                "version": "7.5.5",
                            }
                        },
                    },
                },
            }
        }
        package_map = {
            "@babel/helper-create-class-features-plugin@7.5.5": "7.5.5",
            "features-plugin@^7.5.5": "7.5.5",
        }
        tree = get_dependency_tree(tree_data, package_json, package_map)
        self.assertEqual(
            tree.children[0].name, "@babel/helper-create-class-features-plugin"
        )
        self.assertEqual(tree.children[0].version, "7.5.5")
        self.assertEqual(len(tree.children[0].children), 1)
        self.assertEqual(tree.children[0].children[0].name, "features-plugin")
        self.assertEqual(tree.children[0].children[0].version, "7.5.5")
        self.assertEqual(tree.children[0].children[0].children[0].name, "@babel/plugin")
        self.assertEqual(tree.children[0].children[0].children[0].version, "7.5.5")


if __name__ == "__main__":
    unittest.main()
