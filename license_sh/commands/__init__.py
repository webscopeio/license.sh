import os

import questionary

from license_sh.config import write_config
from license_sh.project_identifier import get_project_types


def config_cmd(path, config):
    projects = config.get("projects", [])
    whitelist = config.get("whitelist", [])

    choices = []
    for dir_name, subdir_list, file_list in os.walk(path, followlinks=False):
        project_types = get_project_types(dir_name)
        if project_types:
            choices.append(questionary.Separator(f"== Path: {dir_name} =="))
            for project_type in project_types:
                choices.append(
                    {
                        "name": f"{project_type.value} project",
                        "value": {"directory": dir_name, "type": project_type.value},
                    }
                )

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
            "type": "confirm",
            "message": "Do you want to modify project paths to be watched by this tool?",
            "name": "change_projects",
            "default": False,
            "when": lambda x: len(projects) > 0,
        },
        {
            "type": "checkbox",
            "qmark": "📦",
            "message": "Select projects to watch",
            "name": "projects",
            "choices": choices,
            "when": lambda x: len(projects) == 0 or x.get("change_projects"),
        },
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

    if "projects" in answers:
        config["projects"] = answers["projects"]
    if "whitelist" in answers:
        config["whitelist"] = answers["whitelist"]

    if write_config(path, config):
        print("Successfully generated .license-sh.json file")
