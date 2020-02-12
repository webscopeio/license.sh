from ..runners.maven import MavenRunner
from ..runners.npm import NpmRunner
from ..runners.python import PythonRunner
from ..runners.yarn import YarnRunner
from ..project_identifier import ProjectType

RUNNERS = {
    ProjectType.PYTHON_PIPENV.value: PythonRunner,
    ProjectType.YARN.value: YarnRunner,
    ProjectType.NPM.value: NpmRunner,
    ProjectType.MAVEN.value: MavenRunner,
}


def run_check(project_to_check: str, path: str, silent: bool, debug: bool):
    runner = RUNNERS.get(project_to_check)
    if not runner:
        return None

    return runner(path, silent, debug).check()
