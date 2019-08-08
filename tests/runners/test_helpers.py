import unittest

from anytree import AnyNode, RenderTree

from license_sh.helpers import flatten_dependency_tree


def get_tree():
  """
  Please always re-generate this comment when changing the tree.
  You can use `print(RenderTree(tree))`

  :return:
  AnyNode(name='Name')
  ├── AnyNode(name='@company/package1', version='1.1.1')
  │   ├── AnyNode(name='package2', version='2.2.2')
  │   │   ├── AnyNode(name='package5', version='5.5.5')
  │   │   └── AnyNode(name='package7', version='7.7.7')
  │   ├── AnyNode(name='package3', version='3.3.3')
  │   │   └── AnyNode(name='package7', version='7.7.6')
  │   ├── AnyNode(name='package4', version='4.4.4')
  │   └── AnyNode(name='package5', version='5.5.5')
  │       └── AnyNode(name='package6', version='6.6.6')
  └── AnyNode(name='package4', version='4.4.4')
      └── AnyNode(name='package6', version='6.6.6')
  """
  tree = AnyNode(name='Name', version='')
  # first level
  package1 = AnyNode(name='@company/package1', parent=tree, version="1.1.1")
  package4 = AnyNode(name='package4', parent=tree, version="4.4.4")

  package2 = AnyNode(name='package2', parent=package1, version="2.2.2")
  AnyNode(name='package5', parent=package2, version="5.5.5")
  AnyNode(name='package7', parent=package2, version="7.7.7")

  package3 = AnyNode(name='package3', parent=package1, version="3.3.3")
  AnyNode(name='package7', parent=package3, version="7.7.6")

  AnyNode(name='package4', parent=package1, version="4.4.4")

  package5 = AnyNode(name='package5', parent=package1, version="5.5.5")
  AnyNode(name='package6', parent=package5, version="6.6.6")

  AnyNode(name='package6', parent=package4, version="6.6.6")
  return tree


class NpmRunnerTestCase(unittest.TestCase):
  def test_dependency_tree_is_flattened(self):
    tree = get_tree()
    dependencies = flatten_dependency_tree(tree)
    self.assertSetEqual(dependencies, {
      ("@company/package1", "1.1.1"),
      ("package2", "2.2.2"),
      ("package3", "3.3.3"),
      ("package4", "4.4.4"),
      ("package5", "5.5.5"),
      ("package6", "6.6.6"),
      ("package7", "7.7.6"),
      ("package7", "7.7.7"),
    })


if __name__ == '__main__':
  unittest.main()
