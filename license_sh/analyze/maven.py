import subprocess
import tempfile
import os
import json
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


def get_analyze_maven_data(directory: str, license_dir: str) -> List:
    """Download licenses xml and based on that download licenses and analyze them

    Args:
        directory (str): Path to the project
        license_dir (str): Directory where to store licenses

    Returns:
        [List]: Result of the askalono analysis
    """
    dep_data = {}
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
        data_root = ET.parse(fname).getroot()
        for dependency in data_root.find("dependencies"):
            dep_id = get_node_id(
                dependency.find("artifactId").text, dependency.find("version").text
            )
            licenses = dependency.find("licenses")
            dep_data[dep_id] = licenses[0].find("url").text

        fetch_maven_licenses(dep_data, license_dir)
        return run_askalono(license_dir, "*")


def get_jar_analyze_dict(directory: str, tmpDir: str) -> Dict:
    """Get dependency jars and analyze them

    Args:
        directory (str): Path to project to check
        tmpDir (str): Directory to store dependency jars

    Returns:
        Dict: "{artifactID}-{version}" as key, analysis result as value
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
    unzip_maven_dependencies(tmpDir)
    jar_analyze = list(
        filter(
            lambda item: item.get("result", {}).get("license", {}).get("name"),
            run_askalono(tmpDir),
        )
    )
    jar_analyze_dict = {}
    for jar_item in jar_analyze:
        dir_name = jar_item.get("path").split(f"{tmpDir}/")[1].split("/")[0]
        jar_analyze_dict[dir_name] = jar_item
    return jar_analyze_dict


def update_analysis_with_jar_analyze(directory: str, analyze_dict: Dict):
    """Update licenses analysis with jar dependency analysis

    Args:
        directory (str): Path to project
        analyze_dict (Dict): analysis to update

    Returns:
        Dict: Updated analysis
    """
    with tempfile.TemporaryDirectory() as dirpath:
        jar_analyze_dict = get_jar_analyze_dict(directory, dirpath)
        for key, item in analyze_dict.items():
            if item.get("name"):
                continue
            name, version = decode_node_id(key)
            jar_analyze_item = jar_analyze_dict.get(f"{name}-{version}")
            if jar_analyze_item:
                item["name"] = jar_analyze_item.get("result", {}).get("name")
                with open(jar_analyze_item.get("path"), "r") as license_file:
                    item["data"] = license_file.read()
    return analyze_dict


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
            dep_id = item.get("path").split("/")[-1]

            with open(item.get("path"), "r") as license_file:
                license_text = license_file.read()
                license_result = item.get("result", {})
                data_dict[dep_id] = {
                    "data": license_text,
                    "name": license_result.get("license", {}).get("name"),
                    "file": item.get("path"),
                }
        return data_dict


def analyze_maven(directory: str, dep_tree: AnyNode) -> AnyNode:
    """Run maven analyze

  Args:
      directory (str): Path to the project
      dep_tree (AnyNode): Dependency tree to update

  Returns:
      [AnyNode]: Updated tree with analyze
  """
    analyze_data = update_analysis_with_jar_analyze(
        directory, get_maven_analyze_dict(directory)
    )
    return add_analyze_to_dep_tree(analyze_data, dep_tree)


def fetch_maven_licenses(dep_data: Dict, dir_path: str):
    """Fetch licenses from url

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
            for dep_id, url in dep_data.items():
                tasks.append(loop.create_task(fetch(session, url, dep_id)))

            for result in asyncio.as_completed(tasks):
                output, dep_id = await result
                file = open(os.path.join(dir_path, dep_id), "w")
                file.write(output)
                file.close()

    asyncio.run(fetch_concurrent())
