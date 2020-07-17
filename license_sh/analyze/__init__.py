from typing import Union

from anytree import AnyNode

from .maven import analyze_maven
from .npm import analyze_npm
from .pipenv import analyze_pipenv
from .yarn import analyze_yarn
from ..project_identifier import ProjectType

ANALYZERS = {
    ProjectType.YARN: analyze_yarn,
    ProjectType.NPM: analyze_npm,
    ProjectType.MAVEN: analyze_maven,
    ProjectType.PYTHON_PIPENV: analyze_pipenv,
}


def run_analyze(project_to_check: ProjectType, path: str, dep_tree: AnyNode) -> Union[AnyNode, None]:
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
