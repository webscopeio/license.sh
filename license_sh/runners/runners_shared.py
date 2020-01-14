import json
import asyncio
import aiohttp as aiohttp

NPM_HOST = "https://registry.npmjs.org"
UNKNOWN = "Unknown"


def fetch_npm_licenses(all_dependencies):
    license_map = {}

    urls = [
        (f"{NPM_HOST}/{dependency}/", version)
        for dependency, version in all_dependencies
    ]

    def get_license(page, version):
        # Extract package license from npm json data
        license_name = page.get("license", UNKNOWN)
        if license_name == UNKNOWN:
            license_name = (
                page.get("versions", {}).get(version, {}).get("license", UNKNOWN)
            )
        return license_name

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
                    license_map[f"{page['name']}@{version}"] = get_license(
                        page, version
                    )

                except json.JSONDecodeError:
                    pass

    asyncio.run(fetch_concurrent(urls))

    return license_map
