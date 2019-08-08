from anytree import PreOrderIter

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
