from anytree import Node, RenderTree, AnyNode, ContStyle
from license_sh.helpers import GREEN, RESET, RED


class ConsoleReporter:
    @staticmethod
    def output(dependency_tree):
        for pre, fill, node in RenderTree(dependency_tree, style=ContStyle()):
            if node.is_root:
                print(" ")
            else:
                color = RED if node.license_problem else GREEN
                print(
                    f"{pre}{node.name} - {node.version} - {color}{node.license}{RESET}"
                )
