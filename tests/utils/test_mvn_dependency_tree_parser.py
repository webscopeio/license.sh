import unittest
from license_sh.utils.MvnDependencyTreeParser import parse 

class ParserTestCase(unittest.TestCase):
  def test_none_tree(self):
    tree = parse(None)
    self.assertIsNone(tree)

  def test_empty_tree(self):
    tree_text = 'com.license:license-tree:jar:0.0.1-SNAPSHOT'
    tree = parse(tree_text)
    self.assertTrue(tree)
    self.assertEqual(tree.name, 'license-tree')
    self.assertEqual(tree.version, '0.0.1-SNAPSHOT')
    self.assertEqual(len(tree.children), 0)

  def test_single_dependency(self):
    tree_text = '''com.license:license-tree:jar:0.0.1-SNAPSHOT
+- org.springframework.boot:spring-boot-starter-data-jpa:jar:2.1.8.RELEASE:compile'''
    tree = parse(tree_text)
    self.assertTrue(tree)
    self.assertEqual(tree.name, 'license-tree')
    self.assertEqual(tree.version, '0.0.1-SNAPSHOT')
    self.assertEqual(len(tree.children), 1)
    self.assertEqual(tree.children[0].name, 'spring-boot-starter-data-jpa')
    self.assertEqual(tree.children[0].version, '2.1.8.RELEASE')

  def test_two_dependencies(self):
    tree_text = '''com.license:license-tree:jar:0.0.1-SNAPSHOT
+- org.springframework.boot:spring-boot-starter-data-jpa:jar:2.1.8.RELEASE:compile
+- org.hibernate:hibernate-core:jar:5.3.11.Final:compile'''
    tree = parse(tree_text)
    self.assertEqual(len(tree.children), 2)
    self.assertEqual(tree.children[1].name, 'hibernate-core')
    self.assertEqual(tree.children[1].version, '5.3.11.Final')

  def test_nested_dependency(self):
    tree_text = '''com.license:license-tree:jar:0.0.1-SNAPSHOT
+- org.springframework.boot:spring-boot-starter-data-jpa:jar:2.1.8.RELEASE:compile
|  +- org.springframework.boot:spring-boot-starter-aop:jar:2.1.8.RELEASE:compile'''
    tree = parse(tree_text)
    self.assertEqual(len(tree.children), 1)
    self.assertEqual(len(tree.children[0].children), 1)
    child = tree.children[0].children[0]
    self.assertEqual(child.name, 'spring-boot-starter-aop')
    self.assertEqual(child.version, '2.1.8.RELEASE')

  def test_two_nested_dependencies(self):
    tree_text = '''com.license:license-tree:jar:0.0.1-SNAPSHOT
+- org.springframework.boot:spring-boot-starter-data-jpa:jar:2.1.8.RELEASE:compile
|  +- org.springframework.boot:spring-boot-starter-aop:jar:2.1.8.RELEASE:compile
|  +- org.aspectj:aspectjweaver:jar:1.9.4:compile'''
    tree = parse(tree_text)    
    self.assertEqual(len(tree.children[0].children), 2)
    child = tree.children[0].children[1]
    self.assertEqual(child.name, 'aspectjweaver')
    self.assertEqual(child.version, '1.9.4')

  def test_nested_nested_dependencies(self):
    tree_text = '''com.license:license-tree:jar:0.0.1-SNAPSHOT
+- org.springframework.boot:spring-boot-starter-data-jpa:jar:2.1.8.RELEASE:compile
|  +- org.springframework.boot:spring-boot-starter-aop:jar:2.1.8.RELEASE:compile
|  |  \- org.aspectj:aspectjweaver:jar:1.9.4:compile'''
    tree = parse(tree_text)    
    self.assertEqual(len(tree.children[0].children), 1)
    child = tree.children[0].children[0].children[0]
    self.assertEqual(child.name, 'aspectjweaver')
    self.assertEqual(child.version, '1.9.4')

  def test_nested_parent_nested_dependencies(self):
    tree_text = '''com.license:license-tree:jar:0.0.1-SNAPSHOT
+- org.springframework.boot:spring-boot-starter-data-jpa:jar:2.1.8.RELEASE:compile
|  \- org.springframework.boot:spring-boot-starter-aop:jar:2.1.8.RELEASE:compile
+- javax.persistence:javax.persistence-api:jar:2.2:compile
|  +- com.zaxxer:HikariCP:jar:3.2.0:compile'''
    tree = parse(tree_text)
    self.assertEqual(len(tree.children), 2)
    child = tree.children[1].children[0]
    self.assertEqual(child.name, 'HikariCP')
    self.assertEqual(child.version, '3.2.0')
    self.assertEqual(child.parent.name, 'javax.persistence-api')

  def test_nested2_parent2_dependencies(self):
    tree_text = '''com.license:license-tree:jar:0.0.1-SNAPSHOT
+- org.springframework.boot:spring-boot-starter-data-jpa:jar:2.1.8.RELEASE:compile
|  \- org.springframework.boot:spring-boot-starter-aop:jar:2.1.8.RELEASE:compile
|  |  \- org.springframework.boot:spring-boot-starter-aop:jar:2.1.8.RELEASE:compile
+- javax.persistence:javax.persistence-api:jar:2.2:compile
|  +- com.zaxxer:HikariCP:jar:3.2.0:compile'''
    tree = parse(tree_text)
    self.assertEqual(len(tree.children), 2)
    child = tree.children[1].children[0]
    self.assertEqual(child.name, 'HikariCP')
    self.assertEqual(child.version, '3.2.0')
    self.assertEqual(child.parent.name, 'javax.persistence-api')

  def test_last_nested_dependencies(self):
    tree_text = '''com.license:license-tree:jar:0.0.1-SNAPSHOT
+- com.vaadin:vaadin-spring-boot-starter:jar:14.0.5:compile
|  +- com.vaadin:vaadin-spring:jar:12.0.6:compile
|  |  +- com.vaadin:flow-server:jar:2.0.12:compile
|  |  |  +- com.vaadin.external.gwt:gwt-elemental:jar:2.8.2.vaadin2:compile
|  |  |  +- commons-fileupload:commons-fileupload:jar:1.3.3:compile
|  |  |  +- commons-io:commons-io:jar:2.5:compile
|  |  |  +- org.jsoup:jsoup:jar:1.11.3:compile
|  |  |  +- com.helger:ph-css:jar:6.1.1:compile
|  |  |  +- com.helger:ph-commons:jar:9.1.2:compile
|  |  |  \- com.vaadin.external:gentyref:jar:1.2.0.vaadin1:compile
|  |  +- com.vaadin:flow-push:jar:2.0.12:compile
|  |  |  \- com.vaadin.external.atmosphere:atmosphere-runtime:jar:2.4.30.slf4jvaadin1:compile
|  |  +- com.vaadin:flow-client:jar:2.0.12:compile
|  |  \- org.springframework:spring-websocket:jar:5.1.9.RELEASE:compile
|  \- com.vaadin:vaadin-core:jar:14.0.5:compile
|     +- com.vaadin:flow-html-components:jar:2.0.12:compile
|     +- com.vaadin:flow-data:jar:2.0.12:compile
|     \- com.vaadin:vaadin-menu-bar-flow:jar:1.0.1:compile
|        \- org.webjars.bowergithub.vaadin:vaadin-menu-bar:jar:1.0.3:compile
\- org.springframework.security:spring-security-test:jar:5.1.6.RELEASE:test
   +- org.springframework.security:spring-security-core:jar:5.1.6.RELEASE:test
   \- org.springframework.security:spring-security-web:jar:5.1.6.RELEASE:test'''

    tree = parse(tree_text)
    self.assertEqual(len(tree.children), 2)
    self.assertEqual(len(tree.children[0].children), 2)
    self.assertEqual(len(tree.children[0].children[0].children), 4)
    self.assertEqual(len(tree.children[0].children[0].children[0].children), 7)
    self.assertEqual(len(tree.children[0].children[0].children[1].children), 1)
    self.assertEqual(len(tree.children[0].children[0].children[3].children), 0)
    self.assertEqual(len(tree.children[0].children[1].children), 3)
    self.assertEqual(len(tree.children[0].children[1].children), 3)
    self.assertEqual(len(tree.children[0].children[1].children[1].children), 0)
    self.assertEqual(len(tree.children[0].children[1].children[2].children), 1)
    self.assertEqual(len(tree.children[1].children), 2)
    self.assertEqual(len(tree.children[1].children[1].children), 0)

    child = tree.children[0].children[1].children[2].children[0]
    self.assertEqual(child.name, 'vaadin-menu-bar')
    self.assertEqual(child.parent.name, 'vaadin-menu-bar-flow')
    self.assertEqual(child.parent.parent.name, 'vaadin-core')
    self.assertEqual(child.parent.parent.parent.name, 'vaadin-spring-boot-starter')
    self.assertEqual(child.parent.parent.parent.parent.name, 'license-tree')





if __name__ == '__main__':
  unittest.main()
