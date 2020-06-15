import subprocess
import os
import json
from license_sh.analyze.analyze_shared import analyze_node_modules, PACKAGE_JSON, UNKNOWN
from license_sh.helpers import get_node_id

def analyze_npm(directory: str):
  subprocess.run(
    ["npm", "ci", "--prefix", directory], stdout=subprocess.PIPE
  )
  license_data = analyze_node_modules(directory)
  data_dict = {}
  for item in license_data:
    path = os.path.join(item.get("path").split('/')[0:-1])
    package_file = os.path.join(path, PACKAGE_JSON)
    if os.path.isfile(package_file):
      with open(package_file, "r") as package_file:
        package_json = json.load(package_file)
        project_name = package_json.get("name", "project_name")
        project_version = package_json.get("version", "unknown")
      
      with open(item.get("path"), "r") as license_file:
        license_text = license_file.read()
        license_result = item.get("result", {})
        data_dict[get_node_id(project_name, project_version)] = {
          "data": license_text,
          "name": license_result.get('license', {}).get("name", UNKNOWN),
        }