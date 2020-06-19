import unittest
from unittest import mock
import xml.etree.ElementTree as ET
from license_sh.analyze.maven import get_analyze_maven_data
from license_sh.helpers import get_node_id

licenses_xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<licenseSummary>
  <dependencies>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-annotations</artifactId>
      <version>2.9.5</version>
      <licenses>
        <license>
          <name>The Apache Software License, Version 2.0</name>
          <url>http://www.apache.org/licenses/LICENSE-2.0.txt</url>
          <distribution>repo</distribution>
          <file>the apache software license, version 2.0 - license-2.0.txt</file>
        </license>
      </licenses>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-core</artifactId>
      <version>2.9.5</version>
      <licenses>
        <license>
          <name>The Apache Software License, Version 2.0</name>
          <url>http://www.apache.org/licenses/LICENSE-2.0.txt</url>
          <distribution>repo</distribution>
          <file>the apache software license, version 2.0 - license-2.0.txt</file>
        </license>
      </licenses>
    </dependency>
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-databind</artifactId>
      <version>2.9.5</version>
      <licenses>
        <license>
          <name>The Apache Software License, Version 2.0</name>
          <url>http://www.apache.org/licenses/LICENSE-2.0.txt</url>
          <distribution>repo</distribution>
          <file>the apache software license, version 2.0 - license-2.0.txt</file>
        </license>
      </licenses>
    </dependency>
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
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.12</version>
      <licenses>
        <license>
          <name>Eclipse Public License 1.0</name>
          <url>http://www.eclipse.org/legal/epl-v10.html</url>
          <distribution>repo</distribution>
          <file>eclipse public license 1.0 - epl-v10.html</file>
        </license>
      </licenses>
    </dependency>
    <dependency>
      <groupId>net.sf.jopt-simple</groupId>
      <artifactId>jopt-simple</artifactId>
      <version>4.6</version>
      <licenses>
        <license>
          <name>The MIT License</name>
          <url>http://www.opensource.org/licenses/mit-license.php</url>
          <distribution>repo</distribution>
          <file>the mit license - mit-license.html</file>
        </license>
      </licenses>
    </dependency>
    <dependency>
      <groupId>org.apache.commons</groupId>
      <artifactId>commons-math3</artifactId>
      <version>3.2</version>
      <licenses>
        <license>
          <name>The Apache Software License, Version 2.0</name>
          <url>http://www.apache.org/licenses/LICENSE-2.0.txt</url>
          <distribution>repo</distribution>
          <file>the apache software license, version 2.0 - license-2.0.txt</file>
        </license>
      </licenses>
    </dependency>
    <dependency>
      <groupId>org.hamcrest</groupId>
      <artifactId>hamcrest-core</artifactId>
      <version>1.3</version>
      <licenses>
        <license>
          <name>New BSD License</name>
          <url>http://www.opensource.org/licenses/bsd-license.php</url>
          <distribution>repo</distribution>
          <file>new bsd license - bsd-license.html</file>
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
    <dependency>
      <groupId>org.openjdk.jmh</groupId>
      <artifactId>jmh-core</artifactId>
      <version>1.20</version>
      <licenses>
        <license>
          <name>GNU General Public License (GPL), version 2, with the Classpath exception</name>
          <url>http://openjdk.java.net/legal/gplv2+ce.html</url>
          <file>gnu general public license (gpl), version 2, with the classpath exception - gplv2+ce.html</file>
        </license>
      </licenses>
    </dependency>
    <dependency>
      <groupId>org.openjdk.jmh</groupId>
      <artifactId>jmh-generator-annprocess</artifactId>
      <version>1.20</version>
      <licenses>
        <license>
          <name>GNU General Public License (GPL), version 2, with the Classpath exception</name>
          <url>http://openjdk.java.net/legal/gplv2+ce.html</url>
          <file>gnu general public license (gpl), version 2, with the classpath exception - gplv2+ce.html</file>
        </license>
      </licenses>
    </dependency>
  </dependencies>
</licenseSummary>"""

class AnalyzeMavenTestCase(unittest.TestCase):

  @mock.patch("xml.etree.ElementTree.parse")
  @mock.patch("license_sh.analyze.maven.fetch_maven_licenses")
  @mock.patch("license_sh.analyze.maven.subprocess")
  @mock.patch("license_sh.analyze.analyze_shared.run_askalono")
  def test_get_analyze_maven_data(self, mock_run_askalono, mock_subprocess, mock_fetch_maven_licenses, mock_xml):
    mock_xml.return_value.getroot.return_value = ET.fromstring(licenses_xml)
    result = get_analyze_maven_data('doesnt/matter', 'neither/do/this')
    dep_data, *rest = mock_fetch_maven_licenses.call_args[0]
    self.assertEqual(dep_data.get(get_node_id('gson', '2.8.3')),'http://www.apache.org/licenses/LICENSE-2.0.txt' )

