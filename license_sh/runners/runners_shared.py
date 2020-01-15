import json
import asyncio
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
                    license_map[f"{page['name']}@{version}"] = extract_npm_license(
                        page, version
                    )

                except json.JSONDecodeError:
                    pass

    asyncio.run(fetch_concurrent(urls))

    return license_map
