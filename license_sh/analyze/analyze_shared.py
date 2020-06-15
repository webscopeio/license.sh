from importlib import resources
from license_sh.analyze import lib
from anytree import AnyNode, PreOrderIter
import os
import json
import subprocess

GIT_IGNORE = '.gitignore'
GIT_IGNORE_DISABLED = '.gitignore_disabled'
PACKAGE_JSON = 'package.json'
UNKNOWN = 'unknown'

def analyze_node_modules(directory: str):
  with resources.path(lib, "askalono.linux") as askalono_path:
    result = []
    git_ignore_path = os.path.join(directory, GIT_IGNORE)
    git_ignore_path_disabled = os.path.join(directory, GIT_IGNORE_DISABLED)
    git_ignore_present = os.path.isfile(git_ignore_path)
    try:
      if git_ignore_present:
        os.rename(git_ignore_path, git_ignore_path_disabled)
      output_str = subprocess.run(
          [
              askalono_path,
              "--format",
              "json",
              "crawl",
              directory,
          ],
          stdout=subprocess.PIPE,
      ).stdout.decode("utf-8")
      output_lines = "\n".split(output_str)
      for line in output_lines:
        result.append(json.loads(line))
    finally:
      if git_ignore_present:
        os.rename(git_ignore_path_disabled, git_ignore_path)

    return result

def add_analyze_to_dep_tree(analyze_dict: dict, dep_tree: AnyNode):
  for node in PreOrderIter(dep_tree):
    node_analyze = analyze_dict[id]
    node.license_text = node_analyze.data
    node.license_analyzed = node_analyze.name