#!/usr/bin/env python

from distutils.core import setup

setup(
    name="license_sh",
    version="1.0.4",
    description="Verify software licenses of your open source software",
    author="Jan Vorcak",
    author_email="vorcak@webscope.io",
    url="https://license.sh",
    scripts=["license-sh"],
    packages=[
        "license_sh",
        "license_sh.project_identifier",
        "license_sh.runners",
        "license_sh.runners.npm",
        "license_sh.runners.yarn",
        "license_sh.runners.yarn.js",
        "license_sh.runners.maven",
        "license_sh.runners.python",
        "license_sh.reporters",
        "license_sh.commands",
    ],
    package_data={
        "license_sh": [
            "runners/yarn/js/package.json",
            "runners/yarn/js/yarn.lock",
            "runners/yarn/js/parseYarnLock.js",
            "runners/maven/maven-dependency-plugin-3.1.1-Licensesh.jar",
        ]
    },
    license="MIT",
    install_requires=[
        "anytree",
        "yaspin",
        "aiohttp",
        "PyInquirer",
        "urllib3",
        "docopt",
        "license-expression",
        "pipdeptree",
    ],
)
