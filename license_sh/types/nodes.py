from typing import NamedTuple, List, Optional

from anytree import NodeMixin


class PackageInfo(NamedTuple):
    """
    This named tuple contains information about a package.
    """
    name: str
    version: str


class PackageNode(NodeMixin):
    def __init__(self, name: str, version: str, parent=None):
        super().__init__()
        self.name: str = name
        self.version: str = version
        self.parent: PackageNode = parent


class AnnotatedPackageNode(PackageNode):
    def __init__(self, license_normalized: Optional[str] = None, licenses: List[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.license_normalized = license_normalized
        self.licenses = licenses
