import os
from os import access, R_OK
from os.path import isfile
from enum import Enum


class ProjectType(Enum):
  PYTHON_PIPENV = 'python_pipenv'
  NPM = 'npm'


__file_exists = lambda path: isfile(path) and access(path, R_OK)


def get_project_types(dir_path: str):
  types = []

  # check for python's pipenv
  pipfile_path: str = os.path.join(dir_path, 'Pipfile')
  pipfile_lock_path: str = os.path.join(dir_path, 'Pipfile.lock')

  if __file_exists(pipfile_path) and __file_exists(pipfile_lock_path):
    types += [ProjectType.PYTHON_PIPENV]

  # check for npm
  pipfile_path: str = os.path.join(dir_path, 'package.json')
  pipfile_lock_path: str = os.path.join(dir_path, 'package-lock.json')

  if __file_exists(pipfile_path) and __file_exists(pipfile_lock_path):
    types += [ProjectType.NPM]

  return types
