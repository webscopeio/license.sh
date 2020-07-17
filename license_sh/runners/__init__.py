from ..project_identifier import ProjectType
from ..runners.maven import MavenRunner
from ..runners.npm import NpmRunner
from ..runners.python import PythonRunner
from ..runners.yarn import YarnRunner
from ..types.nodes import PackageNode

RUNNERS = {
    ProjectType.PYTHON_PIPENV: PythonRunner,
    ProjectType.YARN: YarnRunner,
    ProjectType.NPM: NpmRunner,
    ProjectType.MAVEN: MavenRunner,
}


def run_check(project_to_check: ProjectType, path: str, silent: bool, debug: bool) -> PackageNode:
    runner = RUNNERS.get(project_to_check)
    return runner(path, silent, debug).check()
