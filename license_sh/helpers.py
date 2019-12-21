from typing import Tuple, Set, List

from anytree import PreOrderIter, LevelOrderIter, AnyNode
from license_expression import Licensing

try:
    from license_sh_private.normalizer import normalize
except ImportError:

    def normalize(license_expression):
        return license_expression, False


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


def normalize_license_expression(license_text):
    try:
        license = licensing.parse(license_text)
    except:
        normalized_license, normalized = normalize(license_text)
        return normalized_license

    if license is None:
        return None

    if license.isliteral:
        normalized_license, normalized = normalize(license.render())
        return normalized_license

    operator = license.operator.strip()

    return "({})".format(
        f" {operator} ".join(map(normalize_license_expression, license.args))
    )


def annotate_dep_tree(
    tree, whitelist: [str], ignored_packages: [str]
) -> Tuple[AnyNode, Set[str]]:
    """
  An idea of this function is to go through elements from the bottom -> up and
  mark subtree_problem if any of the children has a license_problem or a subtree_problem
  :param tree:
  :param whitelist:
  :param ignored_packages:
  :return: list of licenses not found in a whitelist
  """

    for node in PreOrderIter(tree):
        node.license_normalized = normalize_license_expression(node.license)

    licenses_not_found = set()
    for node in PreOrderIter(tree):
        node.license_problem = (
            not is_license_ok(node.license_normalized, whitelist)
            and node.name not in ignored_packages
        )
        if node.license_problem and node.license:
            licenses_not_found.add(str(node.license_normalized))

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


def get_dependency_tree_with_licenses(
    dep_tree: AnyNode,
    whitelist: List[str],
    ignored_packages: List[str],
    get_full_tree: bool,
) -> Tuple[AnyNode, Set[str]]:
    """
    Constructs the annotated dependency tree that is later given to a reporter.
    :param dep_tree: Dependency tree without licesnes
    :param whitelist: Whitelist of licenses
    :param ignored_packages: Packages where bad licenses should be ignored
    :param get_full_tree: Determines whether we should display the whole tree or just the problematic parts.
    :return:
    """
    annotated_dep_tree, unknown_licenses = annotate_dep_tree(
        dep_tree, whitelist=whitelist, ignored_packages=ignored_packages
    )
    filtered_dependency_tree = (
        annotated_dep_tree if get_full_tree else filter_dep_tree(annotated_dep_tree)
    )
    return filtered_dependency_tree, unknown_licenses
