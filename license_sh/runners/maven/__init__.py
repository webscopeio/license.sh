import tempfile
from contextlib import nullcontext
from os import path
import xml.etree.ElementTree as ET
import subprocess

from anytree import AnyNode, PreOrderIter
from yaspin import yaspin
from typing import Dict
from pathlib import Path
from importlib import resources

from license_sh.runners import maven

DEPENDENCY_JAR = path.join(
    Path(__file__).parent,
    "..",
    "..",
    "..",
    "jar",
    "maven-dependency-plugin-3.1.1-Licensesh.jar",
)
GROUP_ID = "org.apache.maven.plugins"
ARTIFACT_ID = "maven-dependency-plugin"
VERSION = "3.1.1-Licensesh"
MULTI_LICENSE_JOIN = " AND "


def get_dependency_tree_xml(directory: str, debug=False):
    """Get maven dependency tree as xml
  
    Arguments:
      directory {str} -- path to maven project
  
    Returns:
      [xml] -- XML representation of maven dependency tree
    """

    with resources.path(maven, "pom.xml") as maven_path:
        subprocess.run(["mvn", "install", f"-f={maven_path}"], capture_output=not debug)
    with resources.path(
        maven, "maven-dependency-plugin-3.1.1-Licensesh.jar"
    ) as maven_path:
        subprocess.run(
            [
                "mvn",
                "install:install-file",
                f"-Dfile={maven_path}",
                f"-DgroupId={GROUP_ID}",
                f"-DartifactId={ARTIFACT_ID}",
                f"-Dversion={VERSION}",
                f"-Dpackaging=jar",
            ],
            capture_output=not debug,
        )

    with tempfile.NamedTemporaryFile() as tmpfile:
        subprocess.run(
            [
                "mvn",
                f"{GROUP_ID}:{ARTIFACT_ID}:{VERSION}:tree",
                f"-DoutputType=xml",
                f"-DoutputFile={tmpfile.name}",
                "-f",
                directory,
            ],
            capture_output=not debug,
        )
        return ET.parse(tmpfile).getroot()

    return None


def get_license_xml_file(directory: str, debug: bool) -> ET.ElementTree:
    """Get maven xml licenses

    Arguments:
      directory {str} -- path to maven project

    Returns:
      [xml] -- XML representation of maven licenses xml
    """
    with tempfile.TemporaryDirectory() as dirpath:
        fname = path.join(dirpath, "licenses.tmp")
        subprocess.run(
            [
                "mvn",
                "license:download-licenses",
                f"-DlicensesOutputDirectory={dirpath}",
                "-DskipDownloadLicenses=true",
                f"-DlicensesOutputFile={fname}",
                "-f",
                directory,
            ],
            capture_output=not debug,
        )
        return ET.parse(fname).getroot()
    return None


def get_project_name(pom_xml) -> str:
    """Get project name(artifactID)
  
  Arguments:
      pom_xml {xml} -- xml representation of pom.xml
  
  Returns:
      str -- project name parsed from pom.xml
  """
    for child in pom_xml:
        if "artifactId" in child.tag:
            return child.text


def get_project_pom_xml(directory: str):
    """Get xml representation of pom.xml
  
  Arguments:
      directory {str} -- path to maven project
  
  Returns:
      [xml] -- xml representation of pom.xml
  """
    return ET.parse(path.join(directory, "pom.xml")).getroot()


def parse_licenses_xml(xml) -> Dict[str, str]:
    """Parse xml representation of maven licenses xml

  Example:
    {
      "package@1.2.3": "MIT",
      "utilsPackage@1.2.3": "GPL",
      "renderPackage@1.1.1": "APACHE"
    }
  
  
  Arguments:
      xml -- xml representation of maven licenses xml
  
  Returns:
      Dict[str, str] -- Dict with NAME@VERSION as key and license as value
  """
    license_map = {}
    for dependency in xml.find("dependencies"):
        name = "@".join(
            [dependency.find("artifactId").text, dependency.find("version").text]
        )
        licenses = dependency.find("licenses")
        license_name = None
        for license in licenses:
            if license_name is None:
                license_name = license.find("name").text
            else:
                license_name = "({})".format(
                    " AND ".join([license_name, license.find("name").text])
                )
        license_map[name] = license_name

    return license_map


def parse_dependency_xml(xml, parent: AnyNode = None) -> AnyNode:
    """Parse xml representation of maven dependency tree
  
  Arguments:
      xml -- xml representation of maven dependency tree
  
  Keyword Arguments:
      parent {AnyNode} -- Parent node, used in recursive parsing (default: {None})
  
  Returns:
      [AnyNode] -- Parsed xml dependency tree
  """
    if xml is None:
        return None
    root = AnyNode(name=xml.tag, version=xml.get("version"), parent=parent)
    for dependency in xml:
        parse_dependency_xml(dependency, root)
    return root


class MavenRunner:
    """
  This class checks for dependencies in maven projects and fetches license info
  for each of the packages (including transitive dependencies)
  """

    def __init__(self, directory: str, silent: bool, debug: bool):
        self.directory = directory
        self.silent = silent
        self.debug = debug

    def check(self):
        project_name = get_project_name(get_project_pom_xml(self.directory))

        if not self.silent:
            print("===========")
            print(
                f"Initiated License.sh check for Maven project {project_name} located at {self.directory}"
            )
            print("===========")

        with (
            yaspin(text="Getting dependency tree... (First run might take a while)")
            if not self.silent
            else nullcontext()
        ) as sp:
            xml_tree = get_dependency_tree_xml(self.directory, self.debug)

        with (
            yaspin(text="Analysing dependencies ...")
            if not self.silent
            else nullcontext()
        ) as sp:
            dep_tree = parse_dependency_xml(xml_tree)
            license_map = parse_licenses_xml(
                get_license_xml_file(self.directory, self.debug)
            )

        for node in PreOrderIter(dep_tree):
            node.license = license_map.get(f"{node.name}@{node.version}", "")

        return dep_tree, license_map
