from anytree.exporter import JsonExporter

from license_sh.types.nodes import AnnotatedPackageNode


class JSONConsoleReporter:
    @staticmethod
    def output(dependency_tree: AnnotatedPackageNode):
        exporter = JsonExporter(indent=2)
        print(exporter.export(dependency_tree))
        return 0
