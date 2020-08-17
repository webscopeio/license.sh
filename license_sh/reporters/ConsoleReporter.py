from anytree import RenderTree, ContStyle

from license_sh.helpers import GREEN, RESET, RED, BOLD, is_problematic_node
from license_sh.types.nodes import AnnotatedPackageNode

UNKNOWN = "Unknown"


class ConsoleReporter:
    @staticmethod
    def output(dependency_tree: AnnotatedPackageNode):
        for pre, fill, node in RenderTree(dependency_tree, style=ContStyle()):
            if node.is_root:
                print(" ")
            else:
                color = RED if is_problematic_node(node) else GREEN
                normalized_info = (
                    f', normalized as "{BOLD}{color}{node.license_normalized}{RESET}"'
                    if node.license_normalized != node.license
                    and node.license_normalized is not None
                    else ""
                )
                license_info = node.license if node.license else UNKNOWN
                print(
                    f"{pre}{node.name} - {node.version} - {color}{license_info}{RESET}{normalized_info}"
                )
