import subprocess
import tempfile
import os
import json
import copy
import asyncio
import aiohttp as aiohttp
from zipfile import ZipFile
from importlib import resources
import xml.etree.ElementTree as ET
from license_sh.helpers import get_node_id, decode_node_id
from anytree import AnyNode, PreOrderIter
from license_sh.analyze.analyze_shared import (
    get_askalono,
    GLOB,
    run_askalono,
    add_analyze_to_dep_tree,
)
from license_sh.analyze import lib
from typing import Dict, List


def get_licenses_xml(directory: str):
    """Get maven licenses xml

	Args:
		directory (str): Path to the project

	Returns:
		[xml]: Parsed licenses xml
	"""
    with tempfile.TemporaryDirectory() as dirpath:
        fname = os.path.join(dirpath, "licenses.tmp")
        subprocess.run(
            [
                "mvn",
                "license:download-licenses",
                f"-DlicensesOutputDirectory={dirpath}",
                "-DskipDownloadLicenses=true",
                f"-DlicensesOutputFile={fname}",
                "-f",
                directory,
            ],
            capture_output=True,
        )
        return ET.parse(fname).getroot()


def parse_licenses_xml(data_root) -> Dict:
    """Parse maven licenses xml

	Args:
		data_root (xml): Parsed licenses xml

	Returns:
		[Dict]: dependency id as key, licenses url list as value
	"""
    dep_data = {}
    for dependency in data_root.find("dependencies"):
        dep_id = get_node_id(
            dependency.find("artifactId").text, dependency.find("version").text
        )
        licenses = dependency.find("licenses")
        dep_data[dep_id] = []
        for license_data in licenses:
            dep_data[dep_id].append(license_data.find("url").text)
    return dep_data


def call_copy_dependencies(directory: str, tmpDir: str):
    """Call maven copy dependencies command

	Args:
		directory (str): Path to the project
		tmpDir (str): Path where to copy dependencies
	"""
    subprocess.run(
        [
            "mvn",
            "dependency:copy-dependencies",
            f"-DoutputDirectory={tmpDir}",
            "-f",
            directory,
        ],
        capture_output=True,
    )


def get_jar_analyze_dict(tmp_dir: str, analyze_list: List) -> Dict:
    """Parse jar analyze result

	Args:
		tmp_dir (str): Path to the jar location
		analyze_list (List): Analyze results

	Returns:
		[Dict]: Maven dependency id "{name}-{version}" as key, analyze result and license_text as value
	"""
    jar_analyze = list(
        filter(
            lambda item: item.get("result", {}).get("license", {}).get("name"),
            analyze_list,
        )
    )
    jar_analyze_dict = {}
    for jar_item in jar_analyze:
        dir_name = jar_item.get("path").split(f"{tmp_dir}/")[1].split("/")[0]
        if not jar_analyze_dict.get(dir_name):
            jar_analyze_dict[dir_name] = []
        with open(jar_item.get("path"), "r") as license_file:
            jar_analyze_dict[dir_name].append(
                {
                    "name": jar_item.get("result", {}).get("license", {}).get("name"),
                    "data": license_file.read(),
                    "file": jar_item.get("path"),
                }
            )
    return jar_analyze_dict


def get_analyze_maven_data(directory: str, license_dir: str) -> List:
    """Download licenses xml and based on that download licenses and analyze them

	Args:
		directory (str): Path to the project
		license_dir (str): Directory where to store licenses

	Returns:
		[List]: Result of the askalono analysis
	"""
    fetch_maven_licenses(parse_licenses_xml(get_licenses_xml(directory)), license_dir)
    return run_askalono(license_dir, "*")


def get_jar_analyze_data(directory: str) -> Dict:
    """Get dependency jars and analyze them

	Args:
		directory (str): Path to project to check
		tmpDir (str): Directory to store dependency jars

	Returns:
		Dict: "{artifactID}-{version}" as key, analysis result as value
	"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        call_copy_dependencies(directory, tmp_dir)
        unzip_maven_dependencies(tmp_dir)
        return get_jar_analyze_dict(tmp_dir, run_askalono(tmp_dir))


def merge_licenses_analysis_with_jar_analysis(
    licenses_analysis: Dict, jar_analysis: Dict
):
    """Merge licenses analysis with jar dependency analysis

	Args:
		licenses_analysis (Dict): licenses xml analysis
		jar_analysis (Dict): jar dependency analysis

	Returns:
		Dict: Updated analysis
	"""
    result = {}
    for key, value in licenses_analysis.items():
        item = copy.deepcopy(value)
        result[key] = item
        name, version = decode_node_id(key)
        jar_analyze_list = jar_analysis.get(f"{name}-{version}")
        if jar_analyze_list:
            item.extend(jar_analyze_list)
    return result


def unzip_maven_dependencies(directory: str):
    """Unzip jars in the directory

	Args:
		directory (str): Path to the jars location
	"""
    for f in os.listdir(directory):
        if f.endswith(".jar"):
            with ZipFile(os.path.join(directory, f), "r") as zip_ref:
                zip_ref.extractall(os.path.join(directory, f.split(".jar")[0]))


def get_maven_analyze_dict(directory: str) -> Dict:
    """Get maven alanyze dictonary

	Args:
		directory (str): Path to the project

	Returns:
		Dict: Dependency id as key, license text and analyzed license name and value
	"""
    data_dict = {}
    with tempfile.TemporaryDirectory() as dirpath:
        license_data = get_analyze_maven_data(directory, dirpath)
        for item in license_data:
            dep_id = item.get("path").split("/")[-1].split("@")[0]
            if not data_dict.get(dep_id):
                data_dict[dep_id] = []
            with open(item.get("path"), "r") as license_file:
                license_text = license_file.read()
                license_result = item.get("result", {})
                data_dict[dep_id].append(
                    {
                        "data": license_text,
                        "name": license_result.get("license", {}).get("name"),
                    }
                )
        return data_dict


def analyze_maven(directory: str, dep_tree: AnyNode) -> AnyNode:
    """Run maven analyze

  Args:
	  directory (str): Path to the project
	  dep_tree (AnyNode): Dependency tree to update

  Returns:
	  [AnyNode]: Updated tree with analyze
  """
    jar_analysis = get_jar_analyze_data(directory)
    licenses_analysis = get_maven_analyze_dict(directory)
    analyze_data = merge_licenses_analysis_with_jar_analysis(
        licenses_analysis, jar_analysis
    )
    return add_analyze_to_dep_tree(analyze_data, dep_tree)


def fetch_maven_licenses(dep_data: Dict, dir_path: str):
    """Fetch licenses from url

	TODO: Write unittests

	Args:
		dep_data (Dict): dependency data with dep_id as key and url as value
		dir_path (str): path to where to download the files
	"""

    async def fetch(session, url, dep_id):
        async with session.get(url) as resp:
            return await resp.text(), dep_id
            # Catch HTTP errors/exceptions here

    async def fetch_concurrent():
        loop = asyncio.get_event_loop()
        async with aiohttp.ClientSession() as session:
            tasks = []
            for dep_id, urls in dep_data.items():
                for index, url in enumerate(urls):
                    tasks.append(
                        loop.create_task(fetch(session, url, f"{dep_id}@{index}"))
                    )

            for result in asyncio.as_completed(tasks):
                output, dep_id = await result

                with open(os.path.join(dir_path, dep_id), "w") as file:
                    file.write(output)

    asyncio.run(fetch_concurrent())
