#!/usr/bin/env python
"""License.sh

Usage:
  license-sh.py
  license-sh.py init
  license-sh.py ship <name> move <x> <y> [--speed=<kn>]
  license-sh.py ship shoot <x> <y>
  license-sh.py mine (set|remove) <x> <y> [--moored | --drifting]
  license-sh.py (-t | --tree)
  license-sh.py (-h | --help)
  license-sh.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --speed=<kn>  Speed in knots [default: 10].
  --moored      Moored (anchored) mine.
  --drifting    Drifting mine.

"""
import json

from docopt import docopt
from license_sh.runners.npm import NpmRunner
from license_sh.runners.python import PythonRunner

if __name__ == '__main__':
  arguments = docopt(__doc__, version='License.sh')
  if arguments['init']:
    print('Init')
    exit(0)

  # print(arguments)

  try:
    with open('./.license-sh.json') as license_file:
      config = json.load(license_file)
      for project in config['projects']:
        directory = project['directory']
        project_type = project['type']

        # skip if requested
        if project.get('skip', False):
          print(f"⚠️  Skipping {directory}")
          continue

        if project_type == 'npm':
          runner = NpmRunner(directory, config)
        if project_type == 'python':
          runner = PythonRunner(directory, config)
        runner.check()

  except FileNotFoundError:
    # TODO = test - file does not exist
    print('File not found')
    exit(1)
    # TODO = test - no permission to read the file
  except PermissionError:
    print('No permission to read the file .license-sh.json')
    exit(2)

