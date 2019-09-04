from anytree import PreOrderIter, LevelOrderIter, AsciiStyle, RenderTree

RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"


def flatten_dependency_tree(tree):
  # remove the root node
  return set([(node.name, node.version) for node in PreOrderIter(tree) if tree is not node])


def annotate_dep_tree(tree, whitelist: [str]):
  """
  An idea of this function is to go through elements from the bottom -> up and
  mark subtree_problem if any of the children has a license_problem or a subtree_problem
  :param tree:
  :param whitelist:
  :return:
  """
  for node in PreOrderIter(tree):
    node.license_problem = node.license not in whitelist

  for node in list(LevelOrderIter(tree))[::-1]:
    node.subtree_problem = False if node.is_leaf \
      else any(map(lambda x: x.subtree_problem or x.license_problem, node.children))

  return tree
