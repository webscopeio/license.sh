import json
import os

from license_sh.project_identifier import get_project_types


def init_cmd():
    root_dir = "."
    config = {"projects": {}}
    projects = config["projects"]
    for dir_name, subdir_list, file_list in os.walk(root_dir, followlinks=False):
        project_types = get_project_types(dir_name)
        if project_types:
            projects[dir_name] = list(map(lambda x: x.value, project_types))

    with open(".license-sh", "w+") as file:
        file.write(json.dumps(config, sort_keys=True, indent=2))

    print("Successfully generated .license-sh file")
