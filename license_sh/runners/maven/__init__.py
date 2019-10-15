from os import path, getcwd
import xml.etree.ElementTree as ET
import subprocess
from anytree import AnyNode, PreOrderIter
from yaspin import yaspin
import shutil
from typing import Dict
from pathlib import Path

DEPENDENCY_JAR = path.join(Path(__file__).parent, '..', '..', '..', 'jar', 'maven-dependency-plugin-3.1.1-Licensesh.jar')
GROUP_ID = 'org.apache.maven.plugins'
ARTIFACT_ID = 'maven-dependency-plugin'
VERSION = '3.1.1-Licensesh'
MULTI_LICENSE_JOIN = ' AND '
TEST_DIR = path.join(getcwd(), '.license-shTestDir')
DEPENDENCIES_FILE = path.join(TEST_DIR, 'dependencies.txt')
LICENSE_FILE = path.join(TEST_DIR, 'licenses.xml')

def get_dependency_tree_xml(directory: str):
  """Get maven dependency tree as xml
  
  Arguments:
      directory {str} -- path to maven project
  
  Returns:
      [xml] -- XML representation of maven dependency tree
  """
  subprocess.run([
    'mvn',
    'install:install-file',
    f'-Dfile={DEPENDENCY_JAR}',
    f'-DgroupId={GROUP_ID}',
    f'-DartifactId={ARTIFACT_ID}',
    f'-Dversion={VERSION}',
    f'-Dpackaging=jar'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
  )
  subprocess.run([
    'mvn',
    f'{GROUP_ID}:{ARTIFACT_ID}:{VERSION}:tree',
    f'-DoutputType=xml',
    f'-DoutputFile={DEPENDENCIES_FILE}',
    '-f',
    directory],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
  )
  return ET.parse(DEPENDENCIES_FILE).getroot()

def get_license_xml_file(directory: str):
  """Get maven xml licenses
  
  Arguments:
      directory {str} -- path to maven project
  
  Returns:
      [xml] -- XML representation of maven licenses xml
  """
  subprocess.run([
    'mvn',
    'license:download-licenses',
    f'-DlicensesOutputDirectory={TEST_DIR}',
    '-DskipDownloadLicenses=true',
    f'-DlicensesOutputFile={LICENSE_FILE}',
    '-f',
    directory],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
  )
  return ET.parse(LICENSE_FILE).getroot()

def get_project_name(pom_xml) -> str:
  """Get project name(artifactID)
  
  Arguments:
      pom_xml {xml} -- xml representation of pom.xml
  
  Returns:
      str -- project name parsed from pom.xml
  """
  for child in pom_xml:
    if 'artifactId' in child.tag:
      return child.text

def get_project_pom_xml(directory: str):
  """Get xml representation of pom.xml
  
  Arguments:
      directory {str} -- path to maven project
  
  Returns:
      [xml] -- xml representation of pom.xml
  """
  return ET.parse(path.join(directory, 'pom.xml')).getroot()

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
  for dependency in xml.find('dependencies'):
    name = '@'.join([dependency.find('artifactId').text, dependency.find('version').text])
    licenses = dependency.find('licenses')
    licenseName = None
    for license in licenses:
      if licenseName is None:
        licenseName = license.find('name').text
      else:
        licenseName = MULTI_LICENSE_JOIN.join([licenseName, license.find('name').text])
    license_map[name] = licenseName

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
  root = AnyNode(name=xml.tag, version=xml.get('version'), parent=parent)
  for dependency in xml:
    parse_dependency_xml(dependency, root)
  return root

class MavenRunner:
  """
  This class checks for dependencies in maven projects and fetches license info
  for each of the packages (including transitive dependencies)
  """

  def __init__(self, directory: str):
    self.directory = directory
    self.verbose = True

  def check(self):
    project_name = get_project_name(get_project_pom_xml(self.directory))

    if self.verbose:
      print("===========")
      print(f"Initiated License.sh check for Maven project {project_name} located at {self.directory}")
      print("===========")

    with yaspin(text="Analysing dependencies ...") as sp:
      dep_tree = parse_dependency_xml(get_dependency_tree_xml(self.directory))
      license_map = parse_licenses_xml(get_license_xml_file(self.directory))

    with yaspin(text="Cleaning ...") as sp:
      try:
        shutil.rmtree(TEST_DIR)
      except OSError as e:
        print ("Cleaning Error: %s - %s." % (e.filename, e.strerror))

    for node in PreOrderIter(dep_tree):
      node.license = license_map.get(node.name + '@' + node.version, None)

    return dep_tree, license_map
