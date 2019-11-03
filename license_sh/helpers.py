from typing import Tuple, Set

from anytree import PreOrderIter, LevelOrderIter, AnyNode
from license_expression import Licensing

licensing = Licensing()

RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"


def flatten_dependency_tree(tree):
    # remove the root node
    return set(
        [(node.name, node.version) for node in PreOrderIter(tree) if tree is not node]
    )


def is_license_ok(license_text, whitelist):
    """
  Identifies whether license is compliant with the whitelist
  :param license_text: string or licensing object
  :param whitelist: list of strings to compare with
  :return:
  True - if license is compliant.
  False - if it's not compliant.
  None - if there is a parsing error.
  """
    try:
        license = licensing.parse(license_text)
    except:
        return license_text in whitelist

    if license is None:
        return None

    if license.isliteral:
        return license.render() in whitelist

    operator = license.operator.strip()

    fn = {"OR": any, "AND": all}[operator]

    return fn(map(lambda x: is_license_ok(x, whitelist), license.args))


def annotate_dep_tree(tree, whitelist: [str]) -> Tuple[AnyNode, Set[str]]:
    """
  An idea of this function is to go through elements from the bottom -> up and
  mark subtree_problem if any of the children has a license_problem or a subtree_problem
  :param tree:
  :param whitelist:
  :return: list of licenses not found in a whitelist
  """

    licenses_not_found = set()
    for node in PreOrderIter(tree):
        node.license_problem = not is_license_ok(node.license, whitelist)
        if node.license_problem and node.license:
            licenses_not_found.add(str(node.license))

    for node in list(LevelOrderIter(tree))[::-1]:
        node.subtree_problem = (
            False
            if node.is_leaf
            else any(
                map(lambda x: x.subtree_problem or x.license_problem, node.children)
            )
        )

    return tree, licenses_not_found


def filter_dep_tree(tree: AnyNode) -> AnyNode:
    """Filter dependency tree.
    
    Leave only nodes with license problem of itself or children 
    
    Arguments:
        tree {AnyNode} -- Tree to filter
    
    Returns:
        AnyNode -- Filtered tree
    """
    for node in LevelOrderIter(tree):
        node.children = filter(
            lambda subnode: subnode.subtree_problem or subnode.license_problem,
            node.children,
        )

    return tree
