import sys
from typing import List

import questionary

from license_sh.version import __version__
from license_sh.analyze import run_analyze
from . import config_cmd
from ..config import get_config, get_raw_config, whitelist_licenses, ignore_packages
from ..helpers import (
    get_dependency_tree_with_licenses,
    get_problematic_packages_from_analyzed_tree,
)
from ..project_identifier import ProjectType, get_project_types
from ..reporters.ConsoleReporter import ConsoleReporter
from ..reporters.JSONConsoleReporter import JSONConsoleReporter
from ..runners import run_check
from ..types.nodes import PackageNode


def run_license_sh(arguments):
    config_mode = arguments["config"]
    path = arguments["<path>"] or "."
    config_path = arguments["--config"]
    output = arguments["--output"]
    tree = arguments["--tree"]
    analyze = arguments["--dependencies"]
    project_type = arguments["--project"]
    debug = arguments["--debug"]
    interactive = bool(arguments["--interactive"])

    path_to_config: str = config_path if config_path else path

    if interactive and output == "json":
        print("You can't run in interactive mode while specifying json as an output")
        exit(1)

    if config_mode:
        exit(config_cmd(path, get_raw_config(path_to_config)))

    silent = output == "json" or debug
    whitelist, ignored_packages_map, overridden_packages_map = get_config(path_to_config)

    # docopt guarantees that output variable contains either console or json
    Reporter = {"console": ConsoleReporter, "json": JSONConsoleReporter}[output]

    supported_projects = [e.value for e in ProjectType]
    project_list = get_project_types(path)
    project_list_str: List[str] = [x.value for x in project_list]

    if len(project_list_str) == 0:
        print(
            f"None of currently supported projects found. Supported {supported_projects}",
            file=sys.stderr,
        )
        exit(2)

    project_to_check: ProjectType = ProjectType(project_type) if project_type else project_list[0]

    if project_type:
        if project_type not in supported_projects:
            print(
                f"Specified project '{project_type}' is not supported. Supported {supported_projects}",
                file=sys.stderr,
            )
            exit(2)

        if project_type not in project_list_str:
            print(
                f"Specified project '{project_type}' not found in '{path}'. Found {project_list_str}",
                file=sys.stderr,
            )
            exit(2)

    if not project_type and len(project_list_str) > 1:
        print(
            "Curretly there is no support for multi project/language repositories." +
            f" Found {project_list}. Only '{project_list_str[0]}' will be checked.",
            file=sys.stderr,
        )

    dep_tree: PackageNode = run_check(project_to_check, path, silent, debug)

    dep_tree.data_version = __version__
    dep_tree.project = project_to_check.value

    ignored_packages = ignored_packages_map.get(project_to_check.value, [])
    overridden_packages = overridden_packages_map.get(project_to_check.value, {})

    if analyze:
        analyzed_tree = run_analyze(project_to_check, path, dep_tree)
        if not analyzed_tree:
            print(
                f"Analyze not suported for '{project_to_check}' project",
                file=sys.stderr,
            )

    if not dep_tree:
        print("Unexpected issue, couldn't create dependency tree", file=sys.stderr)
        exit(3)

    (
        filtered_dep_tree,
        licenses_not_found,
        has_issues,
    ) = get_dependency_tree_with_licenses(
        dep_tree,
        whitelist,
        overridden_packages=overridden_packages,
        ignored_packages=ignored_packages,
        get_full_tree=tree,
        analyze=analyze,
    )

    Reporter.output(filtered_dep_tree)

    if licenses_not_found and interactive and questionary.confirm(
        "Do you want to add some of the licenses to your whitelist?"
    ).ask():
        license_whitelist = questionary.checkbox(
            "📋 Which licenses do you want to whitelist?",
            choices=[{"name": license} for license in licenses_not_found],
        ).ask()

        if license_whitelist:
            whitelist_licenses(path_to_config, license_whitelist)

    if has_issues and interactive and questionary.confirm("Do you want to ignore some of the packages?").ask():
        bad_packages = get_problematic_packages_from_analyzed_tree(filtered_dep_tree)
        new_ignored_packages = questionary.checkbox(
            "📋 Which packages do you want to ignore?",
            choices=[{"name": package} for package, version in bad_packages],
        ).ask()
        ignore_packages(path_to_config, project_to_check, new_ignored_packages)

    if not has_issues and not silent:
        print("✅ Your project passed the compliance check 🎉🎉🎉")

    exit(1 if has_issues else 0)
