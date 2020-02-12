import json
import asyncio
import subprocess
import aiohttp as aiohttp
from license_sh.helpers import extract_npm_license

NPM_HOST = "https://registry.npmjs.org"


def fetch_npm_licenses(all_dependencies):
    license_map = {}

    urls = [
        (f"{NPM_HOST}/{dependency}/", version)
        for dependency, version in all_dependencies
    ]

    async def fetch(session, url, version):
        async with session.get(url) as resp:
            return await resp.text(), version
            # Catch HTTP errors/exceptions here

    async def fetch_concurrent(urls):
        loop = asyncio.get_event_loop()
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url, version in urls:
                tasks.append(loop.create_task(fetch(session, url, version)))

            for result in asyncio.as_completed(tasks):
                try:
                    output, version = await result
                    page = json.loads(output)
                    if ("name") in page:
                        license_map[f"{page['name']}@{version}"] = extract_npm_license(
                            page, version
                        )

                except json.JSONDecodeError:
                    pass

    asyncio.run(fetch_concurrent(urls))

    return license_map


def check_command(command: list) -> bool:
    try:
        subprocess.call(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except OSError:
        return False
    return True


def check_yarn():
    if not check_command(["yarn", "--version"]):
        print(f"Missing prerequisite! Yarn is required")
        exit(5)


def check_node():
    if not check_command(["node", "--version"]):
        print(f"Missing prerequisite! Node is required")
        exit(5)


def check_maven():
    if not check_command(["mvn", "--version"]):
        print(f"Missing prerequisite! Maven is required")
        exit(5)
