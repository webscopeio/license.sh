import json
import os
import re
import subprocess
from html.parser import HTMLParser
from importlib import resources
from sys import platform
from typing import Dict, List, Tuple

from anytree import AnyNode, PreOrderIter

from license_sh.analyze import lib

IGNORED_HTML_TAGS = ["style", "script", "head"]
GIT_IGNORE = ".gitignore"
GIT_IGNORE_DISABLED = ".gitignore_disabled"
PACKAGE_JSON = "package.json"
LICENSE_GLOB = "[lL][iI][cC][eE][nN][sScC][eE]*"
GLOB = f"{{{LICENSE_GLOB},[Rr][eE][aA][Dd][Mm][eE]*}}"
UNKNOWN = "unknown"

ASKALONO_BINARY = {
    "linux": "askalono.linux",
    "win32": "askalono.exe",
    "cygwin": "askalono.exe",
    "darwin": "askalono.osx",
}


def get_askalono():
    return ASKALONO_BINARY[platform]


def run_askalono(directory: str, glob: str = GLOB) -> List:
    """ Analyze node modules dependencies

    Args:
      directory (str): Path to the project

    Returns:
      [List]: Result of an node_modules crawling with analyze as List of Dictionaries
    """
    with resources.path(lib, get_askalono()) as askalono_path:
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
                    "--glob",
                    glob,
                    directory,
                ],
                stdout=subprocess.PIPE,
            ).stdout.decode("utf-8")
            output_lines = output_str.split("\n")
            for line in output_lines:
                try:
                    result.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        finally:
            if git_ignore_present:
                os.rename(git_ignore_path_disabled, git_ignore_path)

        return result


def get_node_analyze_dict(directory: str) -> Dict:
    """ Get node_modules analyze with package json data

    Args:
        directory (str): Path to the project

    Returns:
        [Dict]: Project id as a key and Dict with license text and analyzed license name
    """
    data_dict: Dict[Tuple[str, str], List[Dict[str, str]]] = {}
    license_data = run_askalono(directory)
    for item in license_data:
        *path_to_dependency, license_file = item.get("path").split("/")
        path = os.path.join(*path_to_dependency)
        package_file_path = os.path.join(path, PACKAGE_JSON)
        if os.path.isfile(package_file_path):
            with open(package_file_path, "r") as package_file:
                package_json = json.load(package_file)
                node_id = (
                    package_json.get("name", "project_name"),
                    package_json.get("version", "unknown"),
                )

            if not data_dict.get(node_id):
                data_dict[node_id] = []

            if item.get("error", None):
                continue

            with open(item.get("path"), "r") as license_file:
                license_text = license_file.read()
                license_result = item.get("result", {})
                *path_to_file, file_name = item.get("path").split("/")
                if license_text in [
                    item.get("data") for item in data_dict.get(node_id, [])
                ]:
                    continue
                data_dict[node_id].append(
                    {
                        "data": license_text,
                        "name": license_result.get("license", {}).get("name"),
                        "file": file_name,
                    }
                )
    return data_dict


def add_analyze_to_dep_tree(analyze_dict: Dict, dep_tree: AnyNode):
    """Add analyze result to the nodes in the dependency tree

    Args:
        analyze_dict (Dict): Result of the node_modules analyze
        dep_tree (AnyNode): Dependency tree to update
    """
    for node in PreOrderIter(dep_tree):
        node_analyze_list = analyze_dict.get((node.name, node.version))
        node.analyze = []
        if not node_analyze_list:
            continue
        for node_analyze in node_analyze_list:
            if re.match(LICENSE_GLOB, node_analyze.get("file", "")) or node_analyze.get(
                "name"
            ):
                node_analyze.pop("file", None)
                node.analyze.append(node_analyze)
    return dep_tree


def transform_html(html_text: str, ignored_tags: List = IGNORED_HTML_TAGS) -> str:
    """Transform html/xml as string into a raw string without tags

    Args:
        htmlText (str): Html/xml string

    Returns:
        str: Raw string without tags
    """

    class HTMLFilter(HTMLParser):
        text = ""
        ignored_tag = None

        def handle_starttag(self, tag, attrs):
            if tag in ignored_tags and not self.ignored_tag:
                self.ignored_tag = tag

        def handle_endtag(self, tag):
            if tag == self.ignored_tag:
                self.ignored_tag = None

        def handle_data(self, data):
            if not self.ignored_tag and len(data.strip()) != 0:
                self.text += "\n" + data if len(self.text) > 0 else data

    html_filter = HTMLFilter()
    html_filter.feed(html_text)
    return html_filter.text
