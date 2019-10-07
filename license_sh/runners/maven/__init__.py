from os import path
import xml.etree.ElementTree as ET
import subprocess
from anytree import AnyNode, PreOrderIter
from yaspin import yaspin
import shutil

def parse_licenses(xml):
  license_map = {}
  for dependency in xml.find('dependencies'):
    name = dependency.find('artifactId').text + '@' + dependency.find('version').text
    licenses = dependency.find('licenses')
    licenseName = None
    for license in licenses:
      if licenseName is None:
        licenseName = license.find('name').text
      else:
        licenseName += ' AND ' + license.find('name').text
    license_map[name] = licenseName

  return license_map

def parse(xml, parent = None):
  if xml is None:
    return None
  root = AnyNode(name=xml.tag, version=xml.get('version'), parent=parent)
  for dependency in xml:
    parse(dependency, root)
  return root

DEPENDENCY_JAR = './jar/maven-dependency-plugin-3.1.1-Licensesh.jar'
GROUP_ID = 'org.apache.maven.plugins'
ARTIFACT_ID = 'maven-dependency-plugin'
VERSION = '3.1.1-Licensesh'

class MavenRunner:
  """
  This class checks for dependencies in maven projects and fetches license info
  for each of the packages (including transitive dependencies)
  """

  def __init__(self, directory: str):
    self.directory = directory
    self.test_directory = path.join(self.directory, '.license-shTestDir')
    self.license_xml_file = path.join(self.test_directory, 'licenses.xml')
    self.dependency_tree_file = path.join(self.test_directory, 'dependencies.txt')
    self.verbose = True
    self.maven_path = path.join(directory, 'pom.xml')

  def check(self):
    pom_xml = ET.parse(self.maven_path).getroot()
    project_name = 'maven project'
    for child in pom_xml:
      if 'name' in child.tag:
        project_name = child.text

    if self.verbose:
      print("===========")
      print(f"Initiated License.sh check for Maven project {project_name} located at {self.directory}")
      print("===========")

    with yaspin(text="Analysing dependencies ...") as sp:
      subprocess.run([
        'mvn',
        'license:download-licenses',
        f'-DlicensesOutputDirectory={self.test_directory}',
        '-DskipDownloadLicenses=true',
        f'-DlicensesOutputFile={self.license_xml_file}',
        '-f',
        self.directory],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
      )
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
        f'-DoutputFile={self.dependency_tree_file}',
        '-f',
        self.directory],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
      )
      dep_tree = parse(ET.parse(self.dependency_tree_file).getroot())
      license_map = parse_licenses(ET.parse(self.license_xml_file))
    with yaspin(text="Cleaning ...") as sp:
      try:
        shutil.rmtree(self.test_directory)
      except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))

    for node in PreOrderIter(dep_tree):
      node.license = license_map.get(node.name + '@' + node.version, None)

    return dep_tree, license_map
