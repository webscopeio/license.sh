import asyncio
import json
import os
import subprocess
from contextlib import nullcontext
from json import JSONDecodeError
from typing import Set, Dict

import aiohttp
from anytree import PreOrderIter
from yaspin import yaspin

from license_sh.helpers import flatten_dependency_tree, get_initiated_text
from license_sh.project_identifier import ProjectType
from license_sh.runners.abstract_runner import AbstractRunner
from license_sh.types.nodes import PackageNode, PackageInfo


def add_nested_dependencies(dep, parent: PackageNode) -> None:
    name = dep["package_name"]
    version = dep["installed_version"]
    dependencies = dep["dependencies"]

    node = PackageNode(name=name, version=version, parent=parent)
    for dep in dependencies:
        add_nested_dependencies(dep, node)


PYPI_HOST = "https://pypi.org/pypi"


class PythonRunner(AbstractRunner):
    def __init__(self, directory: str, silent: bool, debug: bool):
        self.directory = directory
        self.silent = silent
        self.pipfile_path: str = os.path.join(self.directory, "Pipfile")
        self.pipfile_lock_path: str = os.path.join(self.directory, "Pipfile.lock")
        self.debug = debug

    @staticmethod
    def fetch_licenses(all_dependencies: Set[PackageInfo]) -> Dict[PackageInfo, str]:
        license_map = {}

        urls = [
            f"{PYPI_HOST}/{package_name}/{version}/json"
            for package_name, version in all_dependencies
        ]

        async def fetch(session, url):
            async with session.get(url) as resp:
                return await resp.text()
                # Catch HTTP errors/exceptions here

        async def fetch_concurrent(urls):
            loop = asyncio.get_event_loop()
            async with aiohttp.ClientSession() as session:
                tasks = []
                for u in urls:
                    tasks.append(loop.create_task(fetch(session, u)))

                for result in asyncio.as_completed(tasks):
                    try:
                        page = json.loads(await result)
                        info = page.get("info", {})
                        license_map[
                            PackageInfo(name=info.get('name'), version=info.get('version'))
                        ] = info.get("license", "Unknown")
                    except JSONDecodeError:
                        # TODO - investiage why does such a thing happen
                        pass

        asyncio.run(fetch_concurrent(urls))

        return license_map

    def check(self) -> PackageNode:
        if not self.silent:
            print(get_initiated_text(ProjectType.PYTHON_PIPENV, None, self.directory))

        with yaspin(text="Analysing dependencies ...") if not self.silent else nullcontext():
            result = subprocess.run(
                ["pipdeptree", "--json-tree", "--local-only"],
                capture_output=not self.debug,
            )
            dep_tree = json.loads(result.stdout)

            root = PackageNode(name="", version="")

            for dep in dep_tree:
                add_nested_dependencies(dep, root)

            all_dependencies = flatten_dependency_tree(root)

        with yaspin(text="Fetching license info from pypi ...") if not self.silent else nullcontext():
            license_map = PythonRunner.fetch_licenses(all_dependencies)

        for node in PreOrderIter(root):
            node.license = license_map.get(PackageInfo(name=node.name, version=node.version), None)

        return root
