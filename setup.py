#!/usr/bin/env python

from distutils.core import setup

setup(
    name="License.sh",
    version="1.0.0",
    description="Verify software licenses of your open source software",
    author="Jan Vorcak",
    author_email="vorcak@webscope.io",
    url="https://license.sh",
    scripts=["license-sh"],
    packages=[
        "license_sh",
        "license_sh.project_identifier",
        "license_sh.commands",
        "license_sh.runners",
        "license_sh.runners.npm",
        "license_sh.runners.python",
        "license_sh.runners.yarn",
        "license_sh.runners.maven",
        "license_sh.reporters",
    ],
    license="MIT",
    install_requires=[
        "anytree",
        "yaspin",
        "aiohttp",
        "PyInquirer",
        "urllib3",
        "docopt",
    ],
    data_files=[
        ("license_sh/jar/maven-dependency-plugin-3.1.1-Licensesh.jar"),
    ],
)
