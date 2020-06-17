from .npm import analyze_npm
from .yarn import analyze_yarn
from .maven import analyze_maven
from anytree import AnyNode
from ..project_identifier import ProjectType

ANALYZERS = {
    ProjectType.YARN.value: analyze_yarn,
    ProjectType.NPM.value: analyze_npm,
    ProjectType.MAVEN.value: analyze_maven,
}


def run_analyze(project_to_check: str, path: str, dep_tree: AnyNode) -> AnyNode:
    """ Run dependency analyze

    Args:
        project_to_check (str): Project type to check
        path (str): Path to the project directory
        dep_tree (AnyNode): Dependency tree to update with analyzed data

    Returns:
        [AnyNode]: Updated tree or None if unsuported project type
    """
    analyzer = ANALYZERS.get(project_to_check)
    if not analyzer:
        return None

    return analyzer(path, dep_tree)
