import os
from os import access, R_OK
from os.path import isfile
from enum import Enum


class ProjectType(Enum):
    PYTHON_PIPENV = "python_pipenv"
    NPM = "npm"
    MAVEN = "maven"
    YARN = "yarn"


__file_exists = lambda path: isfile(path) and access(path, R_OK)


def get_project_types(dir_path: str) -> [ProjectType]:
    types = []

    # check for python's pipenv
    pipfile_path: str = os.path.join(dir_path, "Pipfile")
    pipfile_lock_path: str = os.path.join(dir_path, "Pipfile.lock")

    if __file_exists(pipfile_path) and __file_exists(pipfile_lock_path):
        types += [ProjectType.PYTHON_PIPENV]

    # check for npm
    pipfile_path: str = os.path.join(dir_path, "package.json")
    pipfile_lock_path: str = os.path.join(dir_path, "package-lock.json")

    if __file_exists(pipfile_path) and __file_exists(pipfile_lock_path):
        types += [ProjectType.NPM]

    # check for maven
    maven_path: str = os.path.join(dir_path, "pom.xml")

    if __file_exists(maven_path):
        types += [ProjectType.MAVEN]
    # check for yarn
    yarn_path: str = os.path.join(dir_path, "package.json")
    yarn_lock_path: str = os.path.join(dir_path, "yarn.lock")
    if __file_exists(yarn_path) and __file_exists(yarn_lock_path):
        types += [ProjectType.YARN]

    return types
