import unittest
import json
from license_sh.runners.npm import parse, parse_licenses

class ParserTestCase(unittest.TestCase):
  def test_none_tree(self):
    tree = parse(None)
    self.assertIsNone(tree)

  def test_empty_tree(self):
    tree_text = '''{
  "name": "license-tree",
  "version": "1.0.0",
  "dependencies": {}
}'''
    tree = parse(json.loads(tree_text))
    self.assertTrue(tree)
    self.assertEqual(tree.name, 'license-tree')
    self.assertEqual(tree.version, '1.0.0')
    self.assertEqual(len(tree.children), 0)

  def test_single_child_tree(self):
    tree_text = '''{
  "name": "license-tree",
  "version": "1.0.0",
  "dependencies": {
    "@babel/core": {
      "name": "@babel/core",
      "version": "1.2.3"
    }
  }
}'''
    tree = parse(json.loads(tree_text))
    self.assertEqual(tree.children[0].name, '@babel/core')
    self.assertEqual(tree.children[0].version, '1.2.3')

  def test_single_nested_child_tree(self):
    tree_text = '''{
  "name": "license-tree",
  "version": "1.0.0",
  "dependencies": {
    "@babel/core": {
      "name": "@babel/core",
      "version": "1.2.3",
      "dependencies": {
        "@babel/nocore": {
          "name": "@babel/nocore",
          "version": "1.1.1"
        }
      }
    }
  }
}'''
    tree = parse(json.loads(tree_text))
    self.assertEqual(tree.children[0].children[0].name, '@babel/nocore')
    self.assertEqual(tree.children[0].children[0].version, '1.1.1')

  def test_multiple_children_tree(self):
    tree_text = '''{
  "name": "license-tree",
  "version": "1.0.0",
  "dependencies": {
    "@babel/core": {
      "name": "@babel/core",
      "version": "1.2.3"
    },
    "@babel/nocore": {
      "name": "@babel/nocore",
      "version": "1.1.1"
    }
  }
}'''
    tree = parse(json.loads(tree_text))
    self.assertEqual(tree.children[1].name, '@babel/nocore')
    self.assertEqual(tree.children[1].version, '1.1.1')

  def test_multiple_nested_children_tree(self):
    tree_text = '''{
  "name": "license-tree",
  "version": "1.0.0",
  "dependencies": {
    "@babel/core": {
      "name": "@babel/core",
      "version": "1.2.3"
    },
    "@babel/nocore": {
      "name": "@babel/nocore",
      "version": "1.1.1",
      "dependencies": {
        "hosted-git-info": {
          "name": "hosted-git-info",
          "version": "3.2.1"
        },
        "semver": {
          "name": "semver",
          "version": "2.1.3"
        }
      }
    }
  }
}'''
    tree = parse(json.loads(tree_text))
    self.assertEqual(tree.children[1].children[0].name, 'hosted-git-info')
    self.assertEqual(tree.children[1].children[0].version, '3.2.1')
    self.assertEqual(tree.children[1].children[1].name, 'semver')
    self.assertEqual(tree.children[1].children[1].version, '2.1.3')

  def test_multiple_nested_children_license_tree(self):
    tree_text = '''{
  "name": "license-tree",
  "version": "1.0.0",
  "dependencies": {
    "@babel/core": {
      "name": "@babel/core",
      "version": "1.2.3",
      "license": "ISC"
    },
    "@babel/nocore": {
      "name": "@babel/nocore",
      "version": "1.1.1",
      "license": "MIT",
      "dependencies": {
        "hosted-git-info": {
          "name": "hosted-git-info",
          "version": "3.2.1",
          "license": "ISC"
        },
        "semver": {
          "name": "semver",
          "version": "2.1.3"
        }
      }
    }
  }
}'''
    license_map = parse_licenses(json.loads(tree_text))
    self.assertEqual(license_map['@babel/core@1.2.3'], 'ISC')
    self.assertEqual(license_map['@babel/nocore@1.1.1'], 'MIT')
    self.assertEqual(license_map['hosted-git-info@3.2.1'], 'ISC')


  def test_child_licenses_tree(self):
    tree_text = '''{
  "name": "license-tree",
  "version": "1.0.0",
  "dependencies": {
    "@babel/core": {
      "name": "@babel/core",
      "version": "1.2.3",
      "licenses": [
        {
          "type": "MIT"
        }
      ]
    }
  }
}'''
    license_map = parse_licenses(json.loads(tree_text))
    self.assertEqual(license_map['@babel/core@1.2.3'], 'MIT')

  def test_child_multiple_licenses_tree(self):
    tree_text = '''{
  "name": "license-tree",
  "version": "1.0.0",
  "dependencies": {
    "@babel/core": {
      "name": "@babel/core",
      "version": "1.2.3",
      "licenses": [
        {
          "type": "MIT"
        },
        {
          "type": "Apache"
        }
      ]
    }
  }
}'''
    license_map = parse_licenses(json.loads(tree_text))
    self.assertEqual(license_map['@babel/core@1.2.3'], 'MIT AND Apache')

  def test_circular_licenses_tree(self):
    tree_text2 = '''{
  "name": "license-tree",
  "version": "1.0.0",
  "dependencies": {
    "@babel/core2": {
      "name": "@babel/core2",
      "version": "1.2.3",
      "dependencies": {
      "@babel/nocore": {
        "name": "@babel/nocore",
        "version": "1.2.3",
        "licenses": "[Circular]"
      }
    },
    "@babel/nocore": {
        "name": "@babel/nocore",
        "version": "1.2.3",
        "licenses": [
          {
            "type": "MIT"
          }
        ]
      }
    }
  }
}'''
    license_map = parse_licenses(json.loads(tree_text2))
    self.assertEqual(license_map['@babel/nocore@1.2.3'], 'MIT')

  def test_reverse_circular_licenses_tree(self):
    tree_text = '''{
  "name": "license-tree",
  "version": "1.0.0",
  "dependencies": {
    "@babel/nocore": {
        "name": "@babel/nocore",
        "version": "1.2.3",
        "licenses": [
          {
            "type": "MIT"
          }
        ]
      }
    },
    "@babel/core": {
      "name": "@babel/core",
      "version": "1.2.3",
      "dependencies": {
      "@babel/nocore": {
        "name": "@babel/nocore",
        "version": "1.2.3",
        "licenses": "[Circular]"
      }
    }
  }
}'''
    license_map = parse_licenses(json.loads(tree_text))
    self.assertEqual(license_map['@babel/nocore@1.2.3'], 'MIT')
