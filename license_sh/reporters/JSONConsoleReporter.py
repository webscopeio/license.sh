from anytree.exporter import JsonExporter


class JSONConsoleReporter:
    @staticmethod
    def output(dependency_tree):
        exporter = JsonExporter(indent=2)
        print(exporter.export(dependency_tree))
        return 0
