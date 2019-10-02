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

def parse(tree_text):
  if not tree_text:
    return None
  raw_lines = tree_text.split('\n')
  root = parse_dependency(raw_lines[0], True)
  parent = root
  for raw_line in raw_lines[1:]:
    if not raw_line.strip():
      break
    dependency = parse_dependency(raw_line)
    new_parent = parent
    while new_parent.level >= dependency.level:
      new_parent = new_parent.parent
    dependency.parent = new_parent
    parent = dependency
  return root

def get_dependency_level(raw_line):
  index = 0
  level = 0
  POS_LENGTH = 3
  while True:
    level += 1
    pos_string = raw_line[index : index+POS_LENGTH]
    if pos_string == '+- ' or pos_string == '\\- ':
      break
    
    index += POS_LENGTH
  return level

def parse_dependency(raw_line, root = False):
  raw_dependency = raw_line if root else raw_line.split('-', 1)[1].strip()
  dependency = raw_dependency.split(':')
  return AnyNode(
    name=dependency[1],
    version=dependency[3],
    level=(0 if root else get_dependency_level(raw_line))
  )

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
        'dependency:tree',
        f'-DoutputFile={self.dependency_tree_file}',
        '-f',
        self.directory],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
      )
      dep_tree = parse(open(self.dependency_tree_file, "r").read())
      license_map = parse_licenses(ET.parse(self.license_xml_file))
    with yaspin(text="Cleaning ...") as sp:
      try:
        shutil.rmtree(self.test_directory)
      except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))

    for node in PreOrderIter(dep_tree):
      delattr(node, 'level')
      node.license = license_map.get(node.name + '@' + node.version, None)

    return dep_tree, license_map
