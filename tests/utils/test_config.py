import unittest

from license_sh.config import get_ignored_packages, get_licenses_whitelist
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
        non_project_type = "nonProjectType"
        ignored_packages[non_project_type] = ["test"]
        ignored_packages_map = get_ignored_packages(ignored_packages)
        self.assertEqual(ignored_packages_map.get(non_project_type), None)

    def test_get_ignored_packages_non_list(self):
        ignored_packages = dict()
        ignored_packages[ProjectType.YARN.value] = "test"
        ignored_packages_map = get_ignored_packages(ignored_packages)
        self.assertEqual(ignored_packages_map.get(ProjectType.YARN.value), [])

    def test_get_ignored_packages_non_str(self):
        ignored_packages = dict()
        ignored_packages[ProjectType.YARN.value] = [1, "test"]
        ignored_packages_map = get_ignored_packages(ignored_packages)
        self.assertEqual(ignored_packages_map.get(ProjectType.YARN.value), ["test"])

    def test_get_ignored_packages_simple(self):
        yarn_ignored = ["test"]
        npm_ignored = ["bubo"]
        ignored_packages = dict()
        ignored_packages[ProjectType.YARN.value] = yarn_ignored
        ignored_packages[ProjectType.NPM.value] = npm_ignored

        ignored_packages_map = get_ignored_packages(ignored_packages)
        self.assertEqual(ignored_packages_map[ProjectType.YARN.value], yarn_ignored)
        self.assertEqual(ignored_packages_map[ProjectType.NPM.value], npm_ignored)
        self.assertEqual(ignored_packages_map[ProjectType.MAVEN.value], [])

    def test_get_licences_whitelist_none(self):
        self.assertEqual(get_licenses_whitelist(None), [])

    def test_get_licences_whitelist_empty(self):
        self.assertEqual(get_licenses_whitelist([]), [])

    def test_get_licences_whitelist_non_str(self):
        self.assertEqual(get_licenses_whitelist([1, "test"]), ["test"])

    def test_get_licences_whitelist_non_simple(self):
        whitelist = ["MIT", "APACHE", "TEST"]
        self.assertEqual(get_licenses_whitelist(whitelist), whitelist)
