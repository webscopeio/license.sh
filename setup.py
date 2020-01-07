#!/usr/bin/env python
import setuptools
from license_sh.version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="license-sh",
    version=__version__,
    author="Jan Vorcak",
    author_email="vorcak@webscope.io",
    description="License checker - verify software licenses of your open source software",
    scripts=["license-sh"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/webscopeio/license.sh",
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    package_data={
        "license_sh": [
            "runners/yarn/js/package.json",
            "runners/yarn/js/yarn.lock",
            "runners/yarn/js/parseYarnLock.js",
            "runners/maven/maven-dependency-plugin-3.1.1-Licensesh.jar",
            "runners/maven/pom.xml",
        ]
    },
    license="MIT",
    install_requires=[
        "anytree",
        "yaspin",
        "aiohttp",
        "urllib3",
        "docopt",
        "license-expression",
        "pipdeptree",
        "questionary",
    ],
)
