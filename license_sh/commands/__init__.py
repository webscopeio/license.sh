import os

import questionary

from license_sh.config import write_config
from license_sh.project_identifier import get_project_types


def config_cmd(path, config):
    whitelist = config.get("whitelist", [])

    default_licenses = [
        "MIT",
        "Apache-2.0",
        "BSD",
        "GPL-2.0",
        "GPL-3.0",
        "LGPL-3.0",
        "VSPL",
        "MPL-2.0",
        "FreeBSD",
        "Zlib",
        "AFL",
        "X11",
        "JSON",
    ]

    questions = [
        {
            "type": "checkbox",
            "qmark": "📋",
            "message": "Select licenses which are OK to be used for your project",
            "name": "whitelist",
            "choices": [
                {"name": license, "checked": license in whitelist}
                for license in default_licenses
            ],
        },
    ]
    answers = questionary.prompt(questions)

    if "whitelist" in answers:
        config["whitelist"] = answers["whitelist"]

    if write_config(path, config):
        print("Successfully generated .license-sh.json file")
