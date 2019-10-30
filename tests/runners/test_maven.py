import unittest
from license_sh.runners.maven import (
    parse_dependency_xml,
    parse_licenses_xml,
    get_project_name,
)
import xml.etree.ElementTree as ET


class ParserTestCase(unittest.TestCase):
    def test_project_name(self):
        pom_xml = """<?xml version="1.0" encoding="UTF-8"?>
<project
  xmlns="http://maven.apache.org/POM/4.0.0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
  http://maven.apache.org/xsd/maven-4.0.0.xsd"
>
  <modelVersion>4.0.0</modelVersion>
  <groupId>link.sharpe</groupId>
  <artifactId>mavenproject1</artifactId>
  <version>1.0-SNAPSHOT</version>
</project>
"""
        name = get_project_name(ET.fromstring(pom_xml))
        self.assertEqual(name, "mavenproject1")

    def test_none_tree(self):
        tree = parse_dependency_xml(None)
        self.assertIsNone(tree)

    def test_empty_tree(self):
        tree_text = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<license-tree version="0.0.1-SNAPSHOT">
</license-tree>
    """
        tree = parse_dependency_xml(ET.fromstring(tree_text))
        self.assertTrue(tree)
        self.assertEqual(tree.name, "license-tree")
        self.assertEqual(tree.version, "0.0.1-SNAPSHOT")
        self.assertEqual(len(tree.children), 0)

    def test_single_child_tree(self):
        tree_text = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<license-tree version="0.0.1-SNAPSHOT">
<spring-boot-starter-data-jpa version="2.1.8.RELEASE" />
</license-tree>
    """
        tree = parse_dependency_xml(ET.fromstring(tree_text))
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].name, "spring-boot-starter-data-jpa")
        self.assertEqual(tree.children[0].version, "2.1.8.RELEASE")

    def test_two_children_tree(self):
        tree_text = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<license-tree version="0.0.1-SNAPSHOT">
  <spring-boot-starter-data-jpa version="2.1.8.RELEASE" />
  <atmosphere-runtime version="2.4.30.slf4jvaadin1"/>
</license-tree>
    """
        tree = parse_dependency_xml(ET.fromstring(tree_text))
        self.assertEqual(len(tree.children), 2)
        self.assertEqual(tree.children[1].name, "atmosphere-runtime")
        self.assertEqual(tree.children[1].version, "2.4.30.slf4jvaadin1")

    def test_nested_child_tree(self):
        tree_text = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<license-tree version="0.0.1-SNAPSHOT">
  <spring-boot-starter-data-jpa version="2.1.8.RELEASE">
    <atmosphere-runtime version="2.4.30.slf4jvaadin1"/>
  </spring-boot-starter-data-jpa>
</license-tree>
    """
        tree = parse_dependency_xml(ET.fromstring(tree_text))
        self.assertEqual(len(tree.children), 1)
        self.assertEqual(tree.children[0].children[0].name, "atmosphere-runtime")
        self.assertEqual(tree.children[0].children[0].version, "2.4.30.slf4jvaadin1")

    def test_nested_children_tree(self):
        tree_text = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<license-tree version="0.0.1-SNAPSHOT">
  <spring-boot-starter-data-jpa version="2.1.8.RELEASE">
    <atmosphere-runtime version="2.4.30.slf4jvaadin1"/>
    <jackson-datatype-jdk8 version="2.9.9"/>
    <vaadin-context-menu-flow version="3.0.2">
      <vaadin-context-menu version="4.3.12"/>
    </vaadin-context-menu-flow>
  </spring-boot-starter-data-jpa>
  <spring-core version="5.1.9.RELEASE">
    <spring-jcl version="5.1.9.RELEASE"/>
  </spring-core>
</license-tree>
    """
        tree = parse_dependency_xml(ET.fromstring(tree_text))
        self.assertEqual(tree.name, "license-tree")
        self.assertEqual(tree.version, "0.0.1-SNAPSHOT")
        self.assertEqual(tree.children[0].name, "spring-boot-starter-data-jpa")
        self.assertEqual(tree.children[0].version, "2.1.8.RELEASE")
        self.assertEqual(tree.children[0].children[0].name, "atmosphere-runtime")
        self.assertEqual(tree.children[0].children[0].version, "2.4.30.slf4jvaadin1")
        self.assertEqual(tree.children[0].children[1].name, "jackson-datatype-jdk8")
        self.assertEqual(tree.children[0].children[1].version, "2.9.9")
        self.assertEqual(tree.children[0].children[2].name, "vaadin-context-menu-flow")
        self.assertEqual(tree.children[0].children[2].version, "3.0.2")
        self.assertEqual(
            tree.children[0].children[2].children[0].name, "vaadin-context-menu"
        )
        self.assertEqual(tree.children[0].children[2].children[0].version, "4.3.12")
        self.assertEqual(tree.children[1].name, "spring-core")
        self.assertEqual(tree.children[1].version, "5.1.9.RELEASE")
        self.assertEqual(tree.children[1].children[0].name, "spring-jcl")
        self.assertEqual(tree.children[1].children[0].version, "5.1.9.RELEASE")

    def test_parse_licenses_xml(self):
        license_text = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<licenseSummary>
  <dependencies>
    <dependency>
      <groupId>antlr</groupId>
      <artifactId>antlr</artifactId>
      <version>2.7.7</version>
      <licenses>
        <license>
          <name>BSD License</name>
          <url>http://www.antlr.org/license.html</url>
          <distribution>repo</distribution>
          <file>bsd license - license.html</file>
        </license>
      </licenses>
    </dependency>
    <dependency>
      <groupId>ch.qos.logback</groupId>
      <artifactId>logback-classic</artifactId>
      <version>1.2.3</version>
      <licenses>
        <license>
          <name>Eclipse Public License - v 1.0</name>
          <url>http://www.eclipse.org/legal/epl-v10.html</url>
          <file>eclipse public license - v 1.0 - epl-v10.html</file>
        </license>
        <license>
          <name>GNU Lesser General Public License</name>
          <url>http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html</url>
          <file>gnu lesser general public license - lgpl-2.1.html</file>
        </license>
      </licenses>
    </dependency>
    <dependency>
      <groupId>ch.qos.logback</groupId>
      <artifactId>logback-core</artifactId>
      <version>1.2.3</version>
      <licenses>
        <license>
          <name>Eclipse Public License - v 1.0</name>
          <url>http://www.eclipse.org/legal/epl-v10.html</url>
          <file>eclipse public license - v 1.0 - epl-v10.html</file>
        </license>
        <license>
          <name>GNU Lesser General Public License</name>
          <url>http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html</url>
          <file>gnu lesser general public license - lgpl-2.1.html</file>
        </license>
      </licenses>
    </dependency>
  </dependencies>
</licenseSummary>
"""

        license_map = parse_licenses_xml(ET.fromstring(license_text))
        self.assertEqual(license_map["antlr@2.7.7"], "BSD License")
        self.assertEqual(
            license_map["logback-classic@1.2.3"],
            "(Eclipse Public License - v 1.0 AND GNU Lesser General Public License)",
        )
        self.assertEqual(
            license_map["logback-core@1.2.3"],
            "(Eclipse Public License - v 1.0 AND GNU Lesser General Public License)",
        )


if __name__ == "__main__":
    unittest.main()
