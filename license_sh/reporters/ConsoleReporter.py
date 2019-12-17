from anytree import Node, RenderTree, AnyNode, ContStyle
from license_sh.helpers import GREEN, RESET, RED, BOLD


class ConsoleReporter:
    @staticmethod
    def output(dependency_tree):
        for pre, fill, node in RenderTree(dependency_tree, style=ContStyle()):
            if node.is_root:
                print(" ")
            else:
                color = RED if node.license_problem else GREEN
                normalized_info = (
                    f', normalized as "{BOLD}{color}{node.license_normalized}{RESET}"'
                    if node.license_normalized != node.license
                    and node.license_normalized is not None
                    else ""
                )
                print(
                    f"{pre}{node.name} - {node.version} - {color}{node.license}{RESET}{normalized_info}"
                )
