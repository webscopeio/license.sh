import unittest
from unittest import mock
from unittest.mock import mock_open
import xml.etree.ElementTree as ET
import aiohttp as aiohttp
from anytree import AnyNode
from license_sh.analyze.maven import (
    get_analyze_maven_data,
    fetch_maven_licenses,
    get_licenses_xml,
    parse_licenses_xml,
    call_copy_dependencies,
    get_jar_analyze_dict,
    get_maven_analyze_dict,
    analyze_maven,
    merge_licenses_analysis_with_jar_analysis,
)
from license_sh.helpers import get_node_id

licenses_xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<licenseSummary>
  <dependencies>
	<dependency>
	  <groupId>com.google.code.gson</groupId>
	  <artifactId>gson</artifactId>
	  <version>2.8.3</version>
	  <licenses>
		<license>
		  <name>Apache 2.0</name>
		  <url>http://www.apache.org/licenses/LICENSE-2.0.txt</url>
		  <file>the apache software license, version 2.0 - license-2.0.txt</file>
		</license>
	  </licenses>
	</dependency>
	<dependency>
	  <groupId>org.javassist</groupId>
	  <artifactId>javassist</artifactId>
	  <version>3.22.0-GA</version>
	  <licenses>
		<license>
		  <name>MPL 1.1</name>
		  <url>http://www.mozilla.org/MPL/MPL-1.1.html</url>
		  <file>mpl 1.1 - mpl-1.1.html</file>
		</license>
		<license>
		  <name>LGPL 2.1</name>
		  <url>http://www.gnu.org/licenses/lgpl-2.1.html</url>
		  <file>lgpl 2.1 - lgpl-2.1.html</file>
		</license>
		<license>
		  <name>Apache License 2.0</name>
		  <url>http://www.apache.org/licenses/</url>
		  <file>apache license 2.0 - licenses.html</file>
		</license>
	  </licenses>
	</dependency>
  </dependencies>
</licenseSummary>"""

ANALYZE_RESULT = [
    {
        "path": "../target/dependencies/react-15.5.4/LICENSE",
        "result": {"score": 0.9993655, "license": {"name": "Apache-2.0"}},
    },
    {
        "path": "../target/dependencies/react-15.5.4/LICENSE-MIT",
        "result": {"score": 0.9993655, "license": {"name": "MIT"}},
    },
    {
        "path": "../target/dependencies/redux-4.4.4-GA/LICENSE",
        "result": {"score": 0.9993655, "license": {"name": "Apache-2.0"}},
    },
    {"path": "../target/dependencies/package-5.5.5/LICENSE", "error": "Error message",},
]


class AnalyzeMavenTestCase(unittest.TestCase):
    @mock.patch("license_sh.analyze.maven.subprocess")
    @mock.patch("xml.etree.ElementTree.parse")
    def test_get_licenses_xml(self, mock_xml, mock_subprocess):
        result = get_licenses_xml("doesnt/matter")
        mock_subprocess.run.assert_called_once()

    def test_parse_licenses_xml(self):
        result = parse_licenses_xml(ET.fromstring(licenses_xml))
        self.assertEqual(
            result.get(get_node_id("gson", "2.8.3")),
            ["http://www.apache.org/licenses/LICENSE-2.0.txt"],
        )
        self.assertEqual(
            result.get(get_node_id("javassist", "3.22.0-GA")),
            [
                "http://www.mozilla.org/MPL/MPL-1.1.html",
                "http://www.gnu.org/licenses/lgpl-2.1.html",
                "http://www.apache.org/licenses/",
            ],
        )

    @mock.patch("license_sh.analyze.maven.subprocess")
    def test_call_copy_dependencies(self, mock_subprocess):
        result = call_copy_dependencies("doesnt/matter", "/tmp/dir")
        mock_subprocess.run.assert_called_once()

    @mock.patch("builtins.open", callable=mock_open(read_data="data"))
    def test_jar_analyze_dict(self, open_mock):
        result = get_jar_analyze_dict("../target/dependencies", ANALYZE_RESULT)
        self.assertEqual(len(result.values()), 2)
        self.assertEqual(result.get("react-15.5.4")[0].get("name"), "Apache-2.0")
        self.assertEqual(result.get("react-15.5.4")[1].get("name"), "MIT")
        self.assertEqual(result.get("redux-4.4.4-GA")[0].get("name"), "Apache-2.0")

    def test_merge_licenses_analysis_with_jar_analysis(self):
        package1 = get_node_id("package_name", "package_version")
        package2 = get_node_id("package_name2", "package_version2")
        licenses_analysis = {
            package1: [{"data": "License text", "name": "MIT", "file": "LICENSE.md",}],
            package2: [{"data": None, "name": None, "file": None,}],
        }

        jar_analysis = {
            "package_name2-package_version2": [
                {"data": "Fancy MIT license text", "name": "MIT",}
            ]
        }
        result = merge_licenses_analysis_with_jar_analysis(
            licenses_analysis, jar_analysis
        )
        self.assertEqual(result.get(package1)[0].get("name"), "MIT")
        self.assertEqual(result.get(package2)[1].get("name"), "MIT")

    @mock.patch("builtins.open", callable=mock_open(read_data="data"))
    @mock.patch("license_sh.analyze.maven.get_analyze_maven_data")
    def test_get_maven_analyze_dict(self, mock_analyze_data, mock_open):
        mock_analyze_data.return_value = [
            {
                "path": "../target/dependencies/react:-:15.5.4@0",
                "result": {"score": 0.9993655, "license": {"name": "Apache-2.0"}},
            },
            {
                "path": "../target/dependencies/react:-:15.5.4@1",
                "result": {"score": 0.9993655, "license": {"name": "MIT"}},
            },
        ]
        result = get_maven_analyze_dict("doesnt/matter")
        self.assertEqual(result.get("react:-:15.5.4")[0].get("name"), "Apache-2.0")
        self.assertEqual(result.get("react:-:15.5.4")[1].get("name"), "MIT")

    @mock.patch("license_sh.analyze.maven.get_jar_analyze_data")
    @mock.patch("license_sh.analyze.maven.get_maven_analyze_dict")
    def test_analyze_maven(
        self, mock_get_maven_analyze_dict, mock_get_jar_analyze_data
    ):
        tree = AnyNode(
            id=get_node_id("root", "1.0.0"),
            children=[
                AnyNode(id=get_node_id("child", "0.0.2-GA")),
                AnyNode(
                    id=get_node_id("child2", "0.0.5"),
                    children=[AnyNode(id=get_node_id("childChild", "9.5.4"))],
                ),
            ],
        )
        mock_get_jar_analyze_data.return_value = {
            "root-1.0.0": [{"data": "License text", "name": "MIT"}],
            "child-0.0.2-GA": [
                {"data": "Apache license", "name": "Apache-2.0"},
                {"data": "MIT license", "name": "MIT"},
            ],
        }
        mock_get_maven_analyze_dict.return_value = {
            get_node_id("root", "1.0.0"): [{"data": "License text", "name": "MIT"}],
            get_node_id("child", "0.0.2-GA"): [],
            get_node_id("child2", "0.0.5"): [],
            get_node_id("childChild", "9.5.4"): [
                {"data": "License text", "name": "Apache-2.0"}
            ],
        }
        result = analyze_maven("doesnt/matter", tree)
        self.assertEqual(
            tree.analyze,
            [
                {"data": "License text", "name": "MIT"},
                {"data": "License text", "name": "MIT"},
            ],
        )
        self.assertEqual(
            tree.children[0].analyze,
            [
                {"data": "Apache license", "name": "Apache-2.0"},
                {"data": "MIT license", "name": "MIT"},
            ],
        )
        self.assertEqual(
            tree.children[1].children[0].analyze,
            [{"data": "License text", "name": "Apache-2.0"}],
        )
