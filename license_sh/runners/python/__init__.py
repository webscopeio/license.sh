import asyncio
import json
import os
import subprocess
from json import JSONDecodeError
from contextlib import nullcontext

import aiohttp
from anytree import AnyNode, PreOrderIter
from yaspin import yaspin

from license_sh.helpers import flatten_dependency_tree


def add_nested_dependencies(dep, parent):
    name = dep["package_name"]
    version = dep["installed_version"]
    depdendencies = dep["dependencies"]

    node = AnyNode(name=name, version=version, parent=parent)
    for dep in depdendencies:
        add_nested_dependencies(dep, node)


PYPI_HOST = "https://pypi.org/pypi"


class PythonRunner:
    def __init__(self, directory: str, silent: bool, debug: bool):
        self.directory = directory
        self.silent = silent
        self.pipfile_path: str = os.path.join(self.directory, "Pipfile")
        self.pipfile_lock_path: str = os.path.join(self.directory, "Pipfile.lock")
        self.debug = debug

    @staticmethod
    def fetch_licenses(all_dependencies):
        license_map = {}

        urls = [
            f"{PYPI_HOST}/{dependency}/{version}/json"
            for dependency, version in all_dependencies
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
                            f"{info.get('name')}@{info.get('version')}"
                        ] = info.get("license", "Unknown")
                    except JSONDecodeError:
                        # TODO - investiage why does such a thing happen
                        pass

        asyncio.run(fetch_concurrent(urls))

        return license_map

    def check(self):
        if not self.silent:
            print("===========")
            print(
                f"Initiated License.sh check for pipenv project located at {self.directory}"
            )
            print("===========")

        with (
            yaspin(text="Analysing dependencies ...")
            if not self.silent
            else nullcontext()
        ) as sp:
            result = subprocess.run(
                ["pipdeptree", "--json-tree", "--local-only"],
                capture_output=not self.debug,
            )
            dep_tree = json.loads(result.stdout)

            root = AnyNode(name="root", version="")

            for dep in dep_tree:
                add_nested_dependencies(dep, root)

            all_dependencies = flatten_dependency_tree(root)

        with (
            yaspin(text="Fetching license info from pypi ...")
            if not self.silent
            else nullcontext()
        ) as sp:
            license_map = PythonRunner.fetch_licenses(all_dependencies)

        for node in PreOrderIter(root):
            node.license = license_map.get(f"{node.name}@{node.version}", None)

        return root, license_map
