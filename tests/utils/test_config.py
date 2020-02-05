import unittest

from license_sh.config import get_ignored_packages
from license_sh.project_identifier import ProjectType

class ConfigRunnerTestCase(unittest.TestCase):
  def test_get_ignored_packages_none(self):
    ignored_packages_map = get_ignored_packages(None)
    self.assertEqual(ignored_packages_map[ProjectType.YARN.value], [])

  def test_get_ignored_packages_empty(self):
    ignored_packages_map = get_ignored_packages(dict())
    self.assertEqual(ignored_packages_map[ProjectType.YARN.value], [])

  def test_get_ignored_packages_non_projectType(self):
    ignored_packages = dict()
    non_project_type = 'nonProjectType'
    ignored_packages[non_project_type] = ['test']
    ignored_packages_map = get_ignored_packages(ignored_packages)
    self.assertEqual(ignored_packages_map.get(non_project_type), None)

  def test_get_ignored_packages_non_list(self):
    ignored_packages = dict()
    ignored_packages[ProjectType.YARN.value] = 'test' 
    ignored_packages_map = get_ignored_packages(ignored_packages)
    self.assertEqual(ignored_packages_map.get(ProjectType.YARN.value), [])

  def test_get_ignored_packages_simple(self):
    yarn_ignored = ['test']
    npm_ignored = ['bubo']
    ignored_packages = dict()
    ignored_packages[ProjectType.YARN.value] = yarn_ignored
    ignored_packages[ProjectType.NPM.value] = npm_ignored

    ignored_packages_map = get_ignored_packages(ignored_packages)
    self.assertEqual(ignored_packages_map[ProjectType.YARN.value], yarn_ignored)
    self.assertEqual(ignored_packages_map[ProjectType.NPM.value], npm_ignored)
    self.assertEqual(ignored_packages_map[ProjectType.MAVEN.value], [])

