import json
import subprocess
from os import path
from anytree import AnyNode, PreOrderIter
from typing import Dict, List, Tuple
from yaspin import yaspin
from contextlib import nullcontext

from importlib import resources

from license_sh.runners.runners_shared import fetch_npm_licenses
from license_sh.runners.yarn import js


def get_yarn_list_json(pathToYarn: str) -> Dict:
    """Get result of 'yarn list --json --silent --no-progress' as json

    Arguments:
        path {str} -- Path to yarn project

    Returns:
        Dict -- Parsed json of command result
    """
    return json.loads(
        (
            subprocess.run(
                [
                    "yarn",
                    "list",
                    "--json",
                    "--silent",
                    "--no-progress",
                    "--cwd",
                    pathToYarn,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        ).stdout
    )


def get_yarn_lock_json(pathToYarn: str) -> Dict:
    """Get yarn lock file as json

    Arguments:
      path {str} -- Path to yarn project

    Returns:
      Dict -- Parsed yarn lock json
    """

    with resources.path(js, ".") as js_path:
        # install script dependency
        subprocess.run(
            ["yarn", "install", "--frozen-lockfile", "--cwd", js_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # run yarn lock parser
        res = json.loads(
            subprocess.run(
                [
                    "node",
                    path.join(js_path, "parseYarnLock.js"),
                    path.join(pathToYarn, "yarn.lock"),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).stdout
        )

        return res


def parse_yarn_lock(json_element: Dict) -> Dict[str, str]:
    """Parse yarn lock json into dict where
    keys are package name + required version and value is locked version
    Example:
      {
        "package@1.2.3": "1.2.3",
        "utilsPackage@^1.2.3": "1.5.0",
        "renderPackage@~1.1.1": "1.1.1"
      }

    Arguments:
        json_element {Dict} -- Root element of json yarn lock

    Returns:
        Dict[str, str] -- Parsed yarn lock into package dict
    """
    return {
        key: dependency.get("version", None)
        for key, dependency in json_element.get("object", {}).items()
    }


def get_name(name: str) -> str:
    """Get package name from package name + required version
    @deprecated

    Example:

    package@1.2.3 -> package
    @bubolia/package@2.2.2 -> @bubolia/package

    Arguments:
        name {str} -- Package name to parse name from

    Returns:
        str -- Name of the package without required version
    """
    *name_arr_with_optional_at_sign, version = name.split("@")
    return "@".join(name_arr_with_optional_at_sign)


def get_name_and_version(name: str) -> Tuple[str, str]:
    *name_arr_with_optional_at_sign, version = name.split("@")
    return "@".join(name_arr_with_optional_at_sign), version


def get_flat_tree(dependencies: List, package_map: Dict[str, str]) -> Dict:
    """Parse yarn list json dependencies and add them locked version

  Example:
  {
    "package@1.2.3": {
      "name": "package",
      "version": "1.2.3",
      dependencies: {
        "utils@1.2.3": {
          "name": "utils",
          "version": "1.2.3",
          dependencies: {}
        }
      }
    },
    "helper@3.2.1": {
      "name": "helper",
      "version": "3.2.1",
      dependencies: {}
    }
  }

  Arguments:
      dependencies {List} -- List of Dicts that represent yarn list.
      package_map {Dict[str, str]} -- Dict to resolve locked versions of packages

  Returns:
      Dict -- Dict representation of yarn flat tree.
  """
    flat_tree = {}
    for dependency in dependencies:
        dep_full_name = dependency.get("name")
        flat_tree[dependency.get("name")] = {
            "name": get_name(dep_full_name),
            "version": package_map.get(dep_full_name),
            "dependencies": get_flat_tree(dependency.get("children", []), package_map),
        }
    return flat_tree


def get_node_from_dependency(dependency: Dict, parent: AnyNode) -> AnyNode:
    """Parse dependency dict into node

  Dependency example:
   {
      "name": "utils",
      "version": "1.2.3",
      "dependencies": {}
    }

  Arguments:
      dependency {Dict} -- Dict representation of dependency
      parent {AnyNode} -- Parent node

  Returns:
      AnyNode -- Parsed node or None if not valid dependency
  """
    dep_version = dependency.get("version")
    dep_name = dependency.get("name")
    if not dep_version or not dep_name:
        return None
    return AnyNode(
        name=dependency.get("name"),
        version=dependency.get("version"),
        parent=parent,
        dependencies=dependency.get("dependencies", {}),
    )


def find_full_dependency(dependencies: Dict, name: str) -> Dict:
    """Find full dependency in dependencies dict

  Full dependency mean dependency that has childs specified

  Arguments:
      dependencies {Dict} -- Dict representation of dependencies, key as name, value as dependency
      name {str} -- Name of node to find

  Returns:
      Dict -- Found dependency or None
  """
    if not dependencies:
        return None
    dependency = dependencies.get(name)
    if not dependency:
        return None
    result = dependency.get("dependencies")
    if result:
        return dependency
    return None


def add_nested_dependencies(dependency: Dict, parent: AnyNode) -> None:
    """Recurcivelly resolve nested dependencies

  Dependency example:
   {
      "name": "utils",
      "version": "1.2.3",
      "dependencies": {}
    }

  Arguments:
      dependency {Dict} -- Dict representation of dependency
      parent {AnyNode} -- Parent node
  """
    for dependency in dependency.get("dependencies", {}).values():
        node = get_node_from_dependency(dependency, parent)
        if not node:
            continue
        dep_name = f"{node.name}@{node.version}"
        dep = None
        checkNode = node.parent
        names = []
        while checkNode.parent:
            full_dep = find_full_dependency(checkNode.dependencies, dep_name)
            if not dep and full_dep:
                node.dependencies = full_dep.get(
                    "dependencies"
                )  # Update own dependencies with correct dependencies
                dep = full_dep

            checkNode = checkNode.parent  # continue for parent
            names.append(checkNode.name)  # save name to prevent cyclic dependency loop

        # Check the root
        full_dep = find_full_dependency(checkNode.dependencies, dep_name)
        if not dep and full_dep:
            node.dependencies = node.dependencies = full_dep.get("dependencies")
            dep = full_dep

        names = names[:-1]  # let's forget about top level
        # If I'm not already in a tree
        if node.name not in names and dep:
            add_nested_dependencies(dep, node)


def get_dependency_tree(
    flat_tree: Dict, package_json: Dict, package_map: Dict
) -> AnyNode:
    """Get dependency tree.

  Arguments:
      flat_tree {Dict} -- Yarn flat tree
      package_json {Dict} -- package.json of yarn project
      package_map {Dict} -- package_map with locked versions

  Returns:
      AnyNode -- Dependency tree
  """
    # Create root node with project info
    root = AnyNode(
        name=package_json.get("name", "package.json"),
        dependencies=flat_tree,
        version=package_json.get("version"),
    )
    # Load root dependencies from package.json
    for dep_name, dep_version in package_json.get("dependencies", {}).items():
        resolved_version = package_map.get(
            f"{dep_name}@{dep_version}"
        )  # Resolve locked version of the package
        dependency = flat_tree.get(
            f"{dep_name}@{resolved_version}"
        )  # Use package full name to get it dependencies
        # Create first level of nodes based on package.json dependencies
        parent = AnyNode(
            name=dep_name,
            version=dependency.get("version"),
            parent=root,
            dependencies=dependency.get("dependencies"),
        )
        add_nested_dependencies(
            dependency, parent
        )  # Add nested dependencies of first level nodes

    # Delete helper dependencies field
    for node in PreOrderIter(root):
        delattr(node, "dependencies")

    return root


class YarnRunner:
    """
    This class checks for dependencies in Yarn projects and fetches license info
    for each of the packages (including transitive dependencies)
    """

    def __init__(self, directory: str, silent: bool, debug: bool):
        self.directory = directory
        self.silent = silent
        self.package_json_path = path.join(directory, "package.json")
        self.yarn_lock_path = path.join(directory, "yarn.lock")
        self.debug = debug

    def check(self):
        with open(self.package_json_path) as package_json_file:
            package_json = json.load(package_json_file)
            project_name = package_json.get("name", "project_name")

        if not self.silent:
            print("===========")
            print(
                f"Initiated License.sh check for YARN project {project_name} located at {self.directory}"
            )
            print("===========")

        with (
            yaspin(text="Analysing dependencies ...")
            if not self.silent
            else nullcontext()
        ) as sp:
            package_map = parse_yarn_lock(get_yarn_lock_json(self.directory))
            flat_tree = get_flat_tree(
                get_yarn_list_json(self.directory).get("data", {}).get("trees", []),
                package_map,
            )
            dep_tree = get_dependency_tree(flat_tree, package_json, package_map)

            flat_dependencies = [get_name_and_version(s) for s in flat_tree.keys()]
            license_map = fetch_npm_licenses(flat_dependencies)

            for node in PreOrderIter(dep_tree):
                node.license = license_map.get(f"{node.name}@{node.version}", None)

        return dep_tree, license_map
