import json
import unittest

from anytree import AnyNode, PreOrderIter
from license_sh.types.nodes import PackageNode
from anytree.exporter import DictExporter

from license_sh.helpers import (
    flatten_dependency_tree,
    annotate_dep_tree,
    is_license_ok,
    is_analyze_ok,
    filter_dep_tree,
    parse_license,
    extract_npm_license,
    override_dependency_tree_nodes,
    override_dependency_node,
    get_npm_license_from_licenses_array,
    is_problematic_node,
    get_problematic_packages_from_analyzed_tree,
)


def get_tree():
    """
  Please always re-generate this comment when changing the tree.
  You can use `print(RenderTree(tree))`

  :return:
  AnyNode(license='MIT', licenses=['MIT'], license_problem=False, name='Name', subtree_problem=True, version='')
  |-- AnyNode(license='MIT', licenses=['MIT'], license_problem=False, name='@company/package1', subtree_problem=True, version='1.1.1')
  |   |-- AnyNode(license='MIT', licenses=['MIT'], license_problem=False, name='package2', subtree_problem=False, version='2.2.2')
  |   |   |-- AnyNode(license='MIT', licenses=['MIT'], license_problem=False, name='package5', subtree_problem=False, version='5.5.5')
  |   |   +-- AnyNode(license='MIT', licenses=['MIT'], license_problem=False, name='package7', subtree_problem=False, version='7.7.7')
  |   |-- AnyNode(license='MIT', licenses=['MIT'], license_problem=False, name='package3', subtree_problem=True, version='3.3.3')
  |   |   +-- AnyNode(license='GPL', licenses=['GPL'], license_problem=True, name='package7', subtree_problem=False, version='7.7.6')
  |   |-- AnyNode(license='MIT', licenses=['MIT'], license_problem=False, name='package4', subtree_problem=False, version='4.4.4')
  |   +-- AnyNode(license='MIT', licenses=['MIT'], license_problem=False, name='package5', subtree_problem=True, version='5.5.5')
  |       +-- AnyNode(license='GPL', license_problem=True, name='package6', subtree_problem=False, version='6.6.6')
  +-- AnyNode(license='MIT', licenses=['MIT'], license_problem=False, name='package4', subtree_problem=True, version='4.4.4')
      +-- AnyNode(license='GPL', licenses=['GPL'], license_problem=True, name='package6', subtree_problem=False, version='6.6.6')

  print(RenderTree(tree, style=AsciiStyle()))
  """
    tree = AnyNode(name="Name", version="", license="MIT", licenses=["MIT"])
    # first level
    package1 = AnyNode(
        name="@company/package1",
        parent=tree,
        version="1.1.1",
        license="MIT",
        licenses=["MIT"],
    )
    package4 = AnyNode(
        name="package4", parent=tree, version="4.4.4", license="MIT", licenses=["MIT"]
    )

    package2 = AnyNode(
        name="package2",
        parent=package1,
        version="2.2.2",
        license="MIT",
        licenses=["MIT"],
    )
    AnyNode(
        name="package5",
        parent=package2,
        version="5.5.5",
        license="MIT",
        licenses=["MIT"],
    )
    AnyNode(
        name="package7",
        parent=package2,
        version="7.7.7",
        license="MIT",
        licenses=["MIT"],
    )

    package3 = AnyNode(
        name="package3",
        parent=package1,
        version="3.3.3",
        license="MIT",
        licenses=["MIT"],
    )
    AnyNode(
        name="package7",
        parent=package3,
        version="7.7.6",
        license="GPL",
        licenses=["GPL"],
    )

    AnyNode(
        name="package4",
        parent=package1,
        version="4.4.4",
        license="MIT",
        licenses=["MIT"],
    )

    package5 = AnyNode(
        name="package5",
        parent=package1,
        version="5.5.5",
        license="MIT",
        licenses=["MIT"],
    )
    AnyNode(
        name="package6",
        parent=package5,
        version="6.6.6",
        license="GPL",
        licenses=["GPL"],
    )

    AnyNode(
        name="package6",
        parent=package4,
        version="6.6.6",
        license="GPL",
        licenses=["GPL"],
    )
    return tree


class HelpersTestCase(unittest.TestCase):
    maxDiff = None

    def test_dependency_tree_is_flattened(self):
        tree = get_tree()
        dependencies = flatten_dependency_tree(tree)
        self.assertSetEqual(
            dependencies,
            {
                ("@company/package1", "1.1.1"),
                ("package2", "2.2.2"),
                ("package3", "3.3.3"),
                ("package4", "4.4.4"),
                ("package5", "5.5.5"),
                ("package6", "6.6.6"),
                ("package7", "7.7.6"),
                ("package7", "7.7.7"),
            },
        )

    def test_bad_licenses_identified(self):
        tree = get_tree()

        whitelist = ["MIT", "Apache-2.0"]
        _, unknown_licenses = annotate_dep_tree(tree, whitelist, [])
        self.assertSetEqual(set({"GPL"}), unknown_licenses)

    def test_annotate_dependency_tree(self):
        tree = get_tree()

        whitelist = ["MIT", "Apache-2.0"]
        annotated_tree, _ = annotate_dep_tree(tree, whitelist, [])

        expected_tree = AnyNode(
            name="Name",
            version="",
            license="MIT",
            licenses=["MIT"],
            analyze_problem=False,
            license_problem=False,
            subtree_problem=True,
            license_normalized="MIT",
        )
        # first level
        package1 = AnyNode(
            name="@company/package1",
            parent=expected_tree,
            version="1.1.1",
            license="MIT",
            licenses=["MIT"],
            analyze_problem=False,
            license_problem=False,
            subtree_problem=True,
            license_normalized="MIT",
        )
        package4 = AnyNode(
            name="package4",
            parent=expected_tree,
            version="4.4.4",
            license="MIT",
            licenses=["MIT"],
            analyze_problem=False,
            license_problem=False,
            subtree_problem=True,
            license_normalized="MIT",
        )

        package2 = AnyNode(
            name="package2",
            parent=package1,
            version="2.2.2",
            license="MIT",
            licenses=["MIT"],
            analyze_problem=False,
            license_problem=False,
            subtree_problem=False,
            license_normalized="MIT",
        )
        AnyNode(
            name="package5",
            parent=package2,
            version="5.5.5",
            license="MIT",
            licenses=["MIT"],
            analyze_problem=False,
            license_problem=False,
            subtree_problem=False,
            license_normalized="MIT",
        )
        AnyNode(
            name="package7",
            parent=package2,
            version="7.7.7",
            license="MIT",
            licenses=["MIT"],
            analyze_problem=False,
            license_problem=False,
            subtree_problem=False,
            license_normalized="MIT",
        )

        package3 = AnyNode(
            name="package3",
            parent=package1,
            version="3.3.3",
            license="MIT",
            licenses=["MIT"],
            analyze_problem=False,
            license_problem=False,
            subtree_problem=True,
            license_normalized="MIT",
        )
        AnyNode(
            name="package7",
            parent=package3,
            version="7.7.6",
            license="GPL",
            licenses=["GPL"],
            analyze_problem=False,
            license_problem=True,
            subtree_problem=False,
            license_normalized="GPL",
        )

        AnyNode(
            name="package4",
            parent=package1,
            version="4.4.4",
            license="MIT",
            licenses=["MIT"],
            analyze_problem=False,
            license_problem=False,
            subtree_problem=False,
            license_normalized="MIT",
        )

        package5 = AnyNode(
            name="package5",
            parent=package1,
            version="5.5.5",
            license="MIT",
            licenses=["MIT"],
            analyze_problem=False,
            license_problem=False,
            subtree_problem=True,
            license_normalized="MIT",
        )
        AnyNode(
            name="package6",
            parent=package5,
            version="6.6.6",
            license="GPL",
            licenses=["GPL"],
            analyze_problem=False,
            license_problem=True,
            subtree_problem=False,
            license_normalized="GPL",
        )

        AnyNode(
            name="package6",
            parent=package4,
            version="6.6.6",
            license="GPL",
            licenses=["GPL"],
            analyze_problem=False,
            license_problem=True,
            subtree_problem=False,
            license_normalized="GPL",
        )

        exporter = DictExporter()
        self.assertDictEqual(
            exporter.export(expected_tree), exporter.export(annotated_tree)
        )

    def test_bad_licenses_identified_are_ignored_by_package_whitelist(self):
        tree = get_tree()
        ignored_packages = ["package7==7.7.6", "package6==6.6.6"]

        whitelist = ["MIT", "Apache-2.0"]
        _, unknown_licenses = annotate_dep_tree(tree, whitelist, ignored_packages)
        self.assertSetEqual(set(), unknown_licenses)

    def test_bad_licenses_identified__one_package_ignored_by_package_whitelist(self):
        tree = get_tree()
        ignored_packages = ["package7"]

        # package 6 still has the "bad" GPL license
        whitelist = ["MIT", "Apache-2.0"]
        _, unknown_licenses = annotate_dep_tree(tree, whitelist, ignored_packages)
        self.assertSetEqual(set({"GPL"}), unknown_licenses)

    def test_is_license_ok_simple(self):
        self.assertEqual(is_license_ok("MIT", ["MIT"]), True)

    def test_is_license_ok_negative(self):
        self.assertEqual(is_license_ok("MIT", [""]), False)

    def test_is_license_ok_brackets(self):
        self.assertEqual(is_license_ok("MIT AND Zlib", ["MIT", "Zlib"]), True)

    def test_is_license_ok_json(self):
        self.assertEqual(
            is_license_ok(
                {
                    "type": "MIT",
                    "url": "https://github.com/thlorenz/bunyan-format/blob/master/LICENSE",
                },
                [
                    "{'type': 'MIT', 'url': 'https://github.com/thlorenz/bunyan-format/blob/master/LICENSE'}"
                ],
            ),
            True,
        )

    def test_parse_license_complex(self):
        self.assertEqual(parse_license("MIT and APACHE"), ["MIT", "APACHE"])

    def test_parse_license_simple(self):
        self.assertEqual(parse_license("MIT"), ["MIT"])

    def test_extract_npm_license_None_data(self):
        name = extract_npm_license(None, None)
        self.assertEqual(name, None)

    def test_extract_npm_license_None_version(self):
        data = json.loads(
            """{
            "name": "name"
        }"""
        )
        name = extract_npm_license(data, "Unknown")
        self.assertEqual(name, None)

    def test_extract_npm_license_simple(self):
        data = json.loads(
            """{
            "name": "name",
            "license": "MIT"
        }"""
        )
        name = extract_npm_license(data, "Unknown")
        self.assertEqual(name, "MIT")

    def test_extract_npm_licenses_global_single_string(self):
        data = json.loads(
            """{
            "name": "name",
            "licenses": ["MIT"]
        }"""
        )
        name = extract_npm_license(data, "Unknown")
        self.assertEqual(name, "MIT")

    def test_extract_npm_licenses_global_single(self):
        data = json.loads(
            """{
            "name": "name",
            "licenses": [{"type":"MIT"}]
        }"""
        )
        name = extract_npm_license(data, "Unknown")
        self.assertEqual(name, "MIT")

    def test_extract_npm_licenses_global_multiple(self):
        data = json.loads(
            """{
            "name": "name",
            "licenses": [{"type":"MIT"}, {"type":"Apache"}]
        }"""
        )
        name = extract_npm_license(data, "Unknown")
        self.assertEqual(name, "MIT AND Apache")

    def test_extract_npm_licenses_global_empty(self):
        data = json.loads(
            """{
            "name": "name",
            "licenses": []
        }"""
        )
        name = extract_npm_license(data, "Unknown")
        self.assertEqual(name, None)

    def test_extract_npm_licenses_specific_version_simple(self):
        data = json.loads(
            """{
            "name": "name",
             "versions": {
                "1.0.0": {
                    "licenses": [{"type":"MIT"}]
                }
            }
        }"""
        )
        name = extract_npm_license(data, "1.0.0")
        self.assertEqual(name, "MIT")

    def test_extract_npm_licenses_specific_version_multiple(self):
        data = json.loads(
            """{
            "name": "name",
             "versions": {
                "1.0.0": {
                    "licenses": [{"type":"MIT"}, {"type":"Apache"}]
                }
            }
        }"""
        )
        name = extract_npm_license(data, "1.0.0")
        self.assertEqual(name, "MIT AND Apache")

    def test_extract_npm_license_from_versions(self):
        data = json.loads(
            """{
            "name": "name",
            "versions": {
                "1.0.0": {
                    "license": "APACHE"
                }
            }
        }"""
        )
        name = extract_npm_license(data, "1.0.0")
        self.assertEqual(name, "APACHE")

    def test_extract_npm_license_version_priority(self):
        data = json.loads(
            """{
            "name": "name",
            "versions": {
                "1.0.0": {
                    "license": "APACHE"
                }
            },
            "license": "MIT"
        }"""
        )
        name = extract_npm_license(data, "1.0.0")
        self.assertEqual(name, "APACHE")

    def test_extract_npm_license_no_versions(self):
        data = json.loads(
            """{
            "name": "name"
        }"""
        )
        name = extract_npm_license(data, "1.0.0")
        self.assertEqual(name, None)

    def test_extract_npm_license_no_version(self):
        data = json.loads(
            """{
            "name": "name",
            "versions": {
                "6.6.6": {
                    "license": "APACHE"
                }
            }
        }"""
        )
        name = extract_npm_license(data, "1.0.0")
        self.assertEqual(name, None)

    def test_extract_npm_license_no_version_license(self):
        data = json.loads(
            """{
            "name": "name",
            "versions": {
                "1.0.0": {}
            }
        }"""
        )
        name = extract_npm_license(data, "1.0.0")
        self.assertEqual(name, None)

    def test_get_npm_license_from_licenses_array_none(self):
        name = get_npm_license_from_licenses_array(None)
        self.assertEqual(name, None)

    def test_get_npm_license_from_licenses_array(self):
        data = json.loads(
            """{
             "licenses": [{"type":"MIT"}, {"type":"Apache"}]
        }"""
        )
        name = get_npm_license_from_licenses_array(data.get("licenses"))
        self.assertEqual(name, "MIT AND Apache")

    def test_get_npm_license_from_licenses_empty(self):
        data = json.loads(
            """{
             "licenses": [{}]
        }"""
        )
        name = get_npm_license_from_licenses_array(data.get("licenses"))
        self.assertEqual(name, None)

    def test_is_analyze_ok_simple(self):
        node = AnyNode(
            licenses=["MIT"], analyze=[{"name": "MIT", "data": "LicenseText"}]
        )
        self.assertEqual(is_analyze_ok(node), True)

    def test_is_analyze_ok_empty(self):
        node = AnyNode(licenses=["MIT"], analyze=[])
        self.assertEqual(is_analyze_ok(node), False)

    def test_is_analyze_ok_empty_2(self):
        node = AnyNode(licenses=[], analyze=[{"name": "MIT", "data": "LicenseText"}])
        self.assertEqual(is_analyze_ok(node), False)

    def test_is_analyze_ok_none_2(self):
        node = AnyNode(licenses=["MIT"])
        self.assertEqual(is_analyze_ok(node), False)

    def test_is_analyze_ok_more_same(self):
        node = AnyNode(
            licenses=["MIT"],
            analyze=[
                {"name": "MIT", "data": "LicenseText"},
                {"name": "MIT", "data": "LicenseText"},
            ],
        )
        self.assertEqual(is_analyze_ok(node), True)

    def test_is_analyze_ok_more_different(self):
        node = AnyNode(
            licenses=["MIT"],
            analyze=[
                {"name": "MIT", "data": "LicenseText"},
                {"name": "Apache2", "data": "LicenseText"},
            ],
        )
        self.assertEqual(is_analyze_ok(node), False)

    def test_is_analyze_ok_more_same_multiple(self):
        node = AnyNode(
            licenses=["Apache2", "MIT"],
            analyze=[
                {"name": "MIT", "data": "LicenseText"},
                {"name": "Apache2", "data": "LicenseText"},
            ],
        )
        self.assertEqual(is_analyze_ok(node), True)

    def test_is_analyze_ok_more_missing(self):
        node = AnyNode(
            licenses=["Apache2", "MIT", "BSD"],
            analyze=[
                {"name": "MIT", "data": "LicenseText"},
                {"name": "Apache2", "data": "LicenseText"},
            ],
        )
        self.assertEqual(is_analyze_ok(node), False)

    def test_is_analyze_ok_more_analyzed(self):
        node = AnyNode(
            licenses=["Apache2", "MIT"],
            analyze=[
                {"name": "MIT", "data": "LicenseText"},
                {"name": "Apache2", "data": "LicenseText"},
                {"name": "BSD", "data": "LicenseText"},
            ],
        )
        self.assertEqual(is_analyze_ok(node), False)

    def test_filter_dep_tree_simple(self):
        tree = AnyNode(children=[AnyNode(subtree_problem=False, license_problem=False)])
        filtered_tree = filter_dep_tree(tree)
        self.assertEqual(len(filtered_tree.children), 0)

    def test_filter_dep_tree_multiple(self):
        tree = AnyNode(
            children=[
                AnyNode(id="good", subtree_problem=False, license_problem=False),
                AnyNode(id="node", subtree_problem=False, license_problem=True),
            ]
        )
        filtered_tree = filter_dep_tree(tree)
        self.assertEqual(len(filtered_tree.children), 1)
        self.assertEqual(filtered_tree.children[0].id, "node")

    def test_is_problematic_node(self):
        node = AnyNode(subtree_problem=False, license_problem=False)
        self.assertFalse(is_problematic_node(node))

        node = AnyNode(subtree_problem=True, license_problem=False)
        self.assertFalse(is_problematic_node(node))
        self.assertTrue(is_problematic_node(node, check_subtree=True))

        node = AnyNode(subtree_problem=False, license_problem=True)
        self.assertTrue(is_problematic_node(node))

    def test_get_problematic_packages_from_analyzed_tree(self):
        tree = get_tree()
        ignored_packages = []

        whitelist = ["MIT", "Apache-2.0"]
        annotated_tree, unknown_licenses = annotate_dep_tree(
            tree, whitelist, ignored_packages
        )
        self.assertSetEqual(
            get_problematic_packages_from_analyzed_tree(annotated_tree),
            {("package7", "7.7.6"), ("package6", "6.6.6"), },
        )

    def test_get_problematic_packages_from_analyzed_tree_with_ignored_package(self):
        tree = get_tree()
        ignored_packages = ["package7"]

        whitelist = ["MIT", "Apache-2.0"]
        annotated_tree, unknown_licenses = annotate_dep_tree(
            tree, whitelist, ignored_packages
        )
        self.assertSetEqual(
            get_problematic_packages_from_analyzed_tree(annotated_tree),
            {("package6", "6.6.6"), },
        )

    def test_override_dependency_node_simple(self):
        overridden_license = 'IAmLicense'
        override_reason = ' I am reason'
        node = PackageNode(
            name="@company/package1",
            version="1.1.1",
        )
        override_dependency_node(node, {
            "license": overridden_license,
            'reason': override_reason
        })
        self.assertEqual(node.license, overridden_license)
        self.assertEqual(node.license_normalized, overridden_license)
        self.assertEqual(node.license_override_reason, override_reason)

    def test_override_dependency_node_license_text(self):
        overridden_license = 'IAmLicense'
        overridden_license_text = 'IAmLicenseTExt'
        node = PackageNode(
            name="@company/package1",
            version="1.1.1",
        )
        override_dependency_node(node, {
            "license": overridden_license,
            "licenseText": overridden_license_text
        }, True)
        self.assertEqual(node.analyze[0], {"data": overridden_license_text, "name": overridden_license})

    def test_override_dependency_node_license_none(self):
        node = PackageNode(
            name="@company/package1",
            version="1.1.1",
        )
        override_dependency_node(node, None)
        self.assertEqual(getattr(node, 'license', None), None)

    def test_override_dependency_tree_nodes_name(self):
        tree = get_tree()
        overridden_license = 'IAmLicense'
        override_package_name = 'package5'
        overridden_packages = {
            f"{override_package_name}": {
                "license": overridden_license
            }
        }
        override_dependency_tree_nodes(tree, overridden_packages)
        at_least_one_found = False
        for node in PreOrderIter(tree):
            if node.name == override_package_name:
                at_least_one_found = True
                self.assertEqual(node.license, overridden_license)
                self.assertEqual(node.license_normalized, overridden_license)
        self.assertEqual(at_least_one_found, True)

    def test_override_dependency_tree_nodes_name_with_version(self):
        tree = get_tree()
        overridden_license = 'IAmLicense'
        override_package_name = 'package4'
        override_package_version = '4.4.4'
        overridden_packages = {
            f"{override_package_name}=={override_package_version}": {
                "license": overridden_license
            }
        }
        override_dependency_tree_nodes(tree, overridden_packages)
        at_least_one_found = False
        for node in PreOrderIter(tree):
            if node.name == override_package_name and node.version == override_package_version:
                at_least_one_found = True
                self.assertEqual(node.license, overridden_license)
                self.assertEqual(node.license_normalized, overridden_license)
        self.assertEqual(at_least_one_found, True)

    def test_override_dependency_tree_nodes_text(self):
        tree = get_tree()
        overridden_license = 'IAmLicense'
        overridden_license_text = 'IAmLicenseText'
        override_package_name = 'package4'
        override_package_version = '4.4.4'
        overridden_packages = {
            f"{override_package_name}=={override_package_version}": {
                "license": overridden_license,
                "licenseText": overridden_license_text
            }
        }
        override_dependency_tree_nodes(tree, overridden_packages, True)
        at_least_one_found = False
        for node in PreOrderIter(tree):
            if node.name == override_package_name and node.version == override_package_version:
                at_least_one_found = True
                self.assertEqual(node.analyze, [{"name": overridden_license, "data": overridden_license_text}])
        self.assertEqual(at_least_one_found, True)


if __name__ == "__main__":
    unittest.main()
