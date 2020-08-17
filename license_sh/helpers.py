from typing import Tuple, Set, List, Optional

from anytree import PreOrderIter, LevelOrderIter, AnyNode
from anytree.exporter import DictExporter
from anytree.importer import DictImporter
from license_expression import Licensing, ExpressionError

from license_sh.normalizer import normalize
from license_sh.project_identifier import ProjectType
from license_sh.types.nodes import PackageNode, PackageInfo, AnnotatedPackageNode
from license_sh.version import __version__

NODE_ID_SEP = ":-:"

licensing = Licensing()

RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"


def get_npm_license_from_licenses_array(licenses_array):
    """
    Extract licenses name from licenses array and join them with AND

     "licenses": [{"type":"MIT"}, {"type":"Apache"}]

    Arguments:
        json_data {json} -- json data to parse license from
        version {str} -- version of the package

    Returns:
        str --  name on the license or Unknown if not found
    """
    if not licenses_array:
        return None

    license_name = None
    for license_item in licenses_array:
        license_item_type = (
            license_item.get("type", None)
            if type(license_item) is dict
            else f"{license_item}"
        )
        if license_name is not None:
            license_name = f"{license_name} AND {license_item_type}"
        else:
            license_name = license_item_type
    return license_name


def extract_npm_license(json_data, version: str):
    """
    Extract license name from npm package data json

    Arguments:
        json_data {json} -- json data to parse license from
        version {str} -- version of the package

    Returns:
        str --  name on the license or Unknown if not found
    """
    if not json_data:
        return None
    version_data = json_data.get("versions", {}).get(version, {})
    licenses_array = version_data.get("licenses")
    if licenses_array:
        return get_npm_license_from_licenses_array(licenses_array)
    license_name = version_data.get("license")
    if license_name:
        return (
            license_name.get("type")
            if type(license_name) is dict
            else f"{license_name}"
        )

    licenses_array = json_data.get("licenses")
    if licenses_array:
        return get_npm_license_from_licenses_array(licenses_array)

    license_name = json_data.get("license")
    if license_name:
        return (
            license_name.get("type")
            if type(license_name) is dict
            else f"{license_name}"
        )

    return None


def flatten_dependency_tree(tree: PackageNode) -> Set[PackageInfo]:
    # remove the root node
    return set(
        [PackageInfo(name=node.name, version=node.version) for node in PreOrderIter(tree) if tree is not node]
    )


def parse_license(license_text: str) -> List[str]:
    """Parse license, if complex, then break it into simple parts

    Arguments:
        license_text {str} -- license str to be parsed

    Returns:
        list -- List of licenses parsed from gived license str
    """
    if license_text is None:
        return []

    try:
        license = licensing.parse(license_text)
    except ExpressionError:
        return [f"{license_text}"]

    if license is None:
        return []

    if license.isliteral:
        return [license.render()]

    licenses: List[str] = []
    for license_arg in license.args:
        licenses = licenses + parse_license(license_arg)

    return licenses


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
    except ExpressionError:
        return f"{license_text}" in whitelist

    if license is None:
        return None

    if license.isliteral:
        return license.render() in whitelist

    operator = license.operator.strip()

    fn = {"OR": any, "AND": all}[operator]

    return fn(map(lambda x: is_license_ok(x, whitelist), license.args))


def is_analyze_ok(node: AnyNode):
    try:
        node_analyze = node.analyze
    except AttributeError:
        return False

    node_analyze_names = {item.get("name") for item in node_analyze}

    if len(node.licenses) != len(node_analyze_names):
        return False

    for analyze_name in node_analyze_names:
        if analyze_name not in node.licenses:
            return False
    return True


def normalize_license_expression(license_text_raw) -> str:
    if license_text_raw is None:
        return ""

    license_text, normalized = normalize(f"{license_text_raw}")

    try:
        license = licensing.parse(license_text)
    except ExpressionError:
        return license_text

    if license is None:
        return ""

    if license.isliteral:
        normalized_license, normalized = normalize(license.render())
        return normalized_license

    operator = license.operator.strip()

    return "({})".format(
        f" {operator} ".join(map(normalize_license_expression, license.args))
    )


def annotate_dep_tree(
        tree: PackageNode, whitelist: List[str], ignored_packages: List[str], analyze: bool = False
) -> Tuple[AnnotatedPackageNode, Set[str]]:
    """
    An idea of this function is to go through elements from the bottom -> up and
    mark subtree_problem if any of the children has a license_problem or a subtree_problem
    :param tree:
    :param whitelist:
    :param ignored_packages:
    :param analyze:
    :return: list of licenses not found in a whitelist
    """

    for node in PreOrderIter(tree):
        node.license_normalized = normalize_license_expression(node.license)
        node.licenses = parse_license(node.license_normalized)

    licenses_not_found = set()
    for node in PreOrderIter(tree):
        node.analyze_problem = analyze and not is_analyze_ok(node)
        node.license_problem = not is_license_ok(
            node.license_normalized, whitelist
        ) and not (
            f"{node.name}=={node.version}" in ignored_packages
            or node.name in ignored_packages
        )

        if node.license_problem and node.licenses:
            for license_not_found in node.licenses:
                if license_not_found not in whitelist:
                    licenses_not_found.add(license_not_found)

    for node in list(LevelOrderIter(tree))[::-1]:
        node.subtree_problem = (
            False
            if node.is_leaf
            else any(
                map(
                    lambda x: x.subtree_problem
                    or x.license_problem
                    or x.analyze_problem,
                    node.children,
                )
            )
        )

    return tree, licenses_not_found


def label_dep_tree(tree: PackageNode, project: ProjectType) -> PackageNode:
    """
    An idea of this function is to go through elements from the bottom -> up and
    add parameters
    :param tree
    :param project type
    :return tree
    """
    for node in PreOrderIter(tree):
        node.project = project.value
        node.id = get_node_id(node.name, node.version)
        node.leaf = node.is_leaf
        node.data_version = __version__

    return tree


def filter_dep_tree(tree: AnnotatedPackageNode) -> AnnotatedPackageNode:
    """Filter dependency tree.

    Leave only nodes with license problem of itself or children

    Arguments:
        tree {AnyNode} -- Tree to filter

    Returns:
        AnyNode -- Filtered tree
    """
    treeCopy = DictImporter().import_(DictExporter().export(tree))
    for node in LevelOrderIter(treeCopy):
        node.children = filter(
            lambda subnode: is_problematic_node(subnode, check_subtree=True),
            node.children,
        )

    return treeCopy


def get_dependency_tree_with_licenses(
    dep_tree: PackageNode,
    whitelist: List[str],
    ignored_packages: List[str],
    get_full_tree: bool,
    analyze: bool = False,
) -> Tuple[AnnotatedPackageNode, Set[str], bool]:
    """
    Constructs the annotated dependency tree that is later given to a reporter.
    :param dep_tree: Dependency tree without licesnes
    :param whitelist: Whitelist of licenses
    :param ignored_packages: Packages where bad licenses should be ignored
    :param get_full_tree: Determines whether we should display the whole tree or just the problematic parts.
    :param analyze: Analyze flag
    :return:
    """
    annotated_dep_tree, unknown_licenses = annotate_dep_tree(
        dep_tree,
        whitelist=whitelist,
        ignored_packages=ignored_packages,
        analyze=analyze,
    )
    filtered_dependency_tree = filter_dep_tree(annotated_dep_tree)
    has_issues = filtered_dependency_tree.height > 0
    dependency_tree = annotated_dep_tree if get_full_tree else filtered_dependency_tree
    return dependency_tree, unknown_licenses, has_issues


def get_node_id(node_name: str, node_version: str) -> str:
    """
    Get node id from name and version
    """
    id_name = node_name.replace("/", ">")
    id_version = node_version.replace("/", ">")
    return f"{id_name}{NODE_ID_SEP}{id_version}"


def decode_node_id(node_id: str) -> List:
    """
    Get name and version from node id
    """
    return node_id.split(NODE_ID_SEP)


def is_problematic_node(node: AnyNode, check_subtree: bool = False) -> bool:
    """
    Determines whether there is an issue with a node.
    :return: True if there is a problem False otherwise
    """
    problematic_node = getattr(node, "license_problem", False) or getattr(
        node, "analyze_problem", False
    )
    if check_subtree:
        return problematic_node or getattr(node, "subtree_problem", False)
    else:
        return problematic_node


def get_problematic_packages_from_analyzed_tree(
    node: AnyNode,
) -> Set[Tuple[str, Optional[str]]]:
    """
    Gets a set of problematic packages with the corresponding versions
    """
    return set(
        [
            (node.name, node.version)
            for node in LevelOrderIter(node)
            if is_problematic_node(node)
        ]
    )


def get_initiated_text(project_type: ProjectType, project_name: Optional[str], dir_path: str) -> str:
    return f"🔍 Initiated license.sh check for {project_type.value} project " + \
           f"{f'{project_name} ' if project_name else ''}located at {dir_path}"
