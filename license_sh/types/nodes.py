from typing import NamedTuple

from anytree import NodeMixin


class PackageInfo(NamedTuple):
    """
    This named tuple contains information about a package.
    """
    name: str
    version: str


class PackageNode(NodeMixin):
    def __init__(self, name: str, version: str, parent: NodeMixin = None):
        super().__init__()
        self.name = name
        self.version = version
        self.parent = parent
