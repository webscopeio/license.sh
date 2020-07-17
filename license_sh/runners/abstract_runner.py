from abc import ABCMeta

from license_sh.types.nodes import PackageNode


class AbstractRunner(metaclass=ABCMeta):
    @property
    def check(self) -> PackageNode:
        pass
