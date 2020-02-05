import questionary
import sys
from . import config_cmd
from ..config import get_config, whitelist_licenses
from ..helpers import get_dependency_tree_with_licenses
from ..project_identifier import ProjectType, get_project_types
from ..reporters.ConsoleReporter import ConsoleReporter
from ..reporters.JSONConsoleReporter import JSONConsoleReporter
from ..runners import run_check

try:
    from license_sh_private.licenses import COMMERCIAL_LICENSES as WHITELIST
except ImportError:
    WHITELIST = []


def run_license_sh(arguments):

    config_mode = arguments["config"]
    path = arguments["<path>"] or "."
    configPath = arguments["--config"]
    output = arguments["--output"]
    tree = arguments["--tree"]
    debug = arguments["--debug"]

    path_to_config = configPath if configPath else path
    config = get_config(path_to_config)

    config_ignored_packages = config.get("ignored_packages", {})
    ignored_packages_map = {
        e.value: config_ignored_packages.get(e.value, {}) for e in ProjectType
    }

    whitelist = WHITELIST + config.get("whitelist", [])

    if config_mode:
        config_cmd(path, config)
        exit(0)

    silent = output == "json" or debug

    # docopt guarantees that output variable contains either console or json
    Reporter = {"console": ConsoleReporter, "json": JSONConsoleReporter}[output]

    ignored_packages = []
    project_list = [e.value for e in get_project_types(path)]

    if len(project_list) == 0:
        supported_projects = [e.value for e in ProjectType]
        print(
            f"None of currently supported projects found. Supported {supported_projects}",
            file=sys.stderr,
        )
        exit(2)

    if len(project_list) > 1:
        print(
            f"Curretly there is no support for multi project/language repositories. Found {project_types}. Only '{project_types[0]}' will be checked.",
            file=sys.stderr,
        )

    project_to_check = project_list[0]
    dep_tree = run_check(project_to_check, path, silent, debug)
    ignored_packages = ignored_packages_map.get(project_to_check, [])
    if not dep_tree:
        print(f"Unexpected issue, couldn't create dependency tree", file=sys.stderr)
        exit(3)

    (
        filtered_dep_tree,
        licenses_not_found,
        has_issues,
    ) = get_dependency_tree_with_licenses(
        dep_tree, whitelist, ignored_packages=ignored_packages, get_full_tree=tree
    )

    Reporter.output(filtered_dep_tree)

    if licenses_not_found and output != "json":
        manual_add: bool = questionary.confirm(
            "Do you want to add some of the licenses to your whitelist?"
        ).ask()

        if manual_add:
            license_whitelist = questionary.checkbox(
                "📋 Which licenses do you want to whitelist?",
                choices=[{"name": license} for license in licenses_not_found],
            ).ask()
            if license_whitelist:
                whitelist_licenses(path_to_config, license_whitelist)

                config = get_config(path)
                (
                    filtered_dep_tree,
                    licenses_not_found,
                    has_issues,
                ) = get_dependency_tree_with_licenses(
                    dep_tree,
                    config.get("whitelist", []),
                    ignored_packages=ignored_packages,
                    get_full_tree=tree,
                )
                Reporter.output(filtered_dep_tree)

    exit(1 if has_issues else 0)
