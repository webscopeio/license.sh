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
from license_sh.analyze.analyze_shared import get_askalono, GLOB
from license_sh.analyze import lib
from typing import Dict, List


def get_analyze_maven_data(directory: str, license_dir: str):
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
        return analyze_maven_dependencies(license_dir)

def copy_maven_dependencies(directory: str, dependency_dir: str):
    subprocess.run(
        [
            "mvn",
            "dependency:copy-dependencies",
            f"-DoutputDirectory={dependency_dir}",
            "-f",
            directory,
        ],
        capture_output=True,
    )

def get_jar_dependency_analyze(directory: str, analyze_dict: Dict):
    with tempfile.TemporaryDirectory() as dirpath:
        copy_maven_dependencies(directory, dirpath)
        unzip_maven_dependencies(dirpath)
        jar_analyze = list(filter(lambda item: item.get('result', {}).get('license', {}).get('name'), analyze_maven_jar_dependencies(dirpath)))
        jar_analyze_dict = {}
        for jar_item in jar_analyze:
            dir_name = jar_item.get('path').split(f"{dirpath}/")[1].split('/')[0]
            jar_analyze_dict[dir_name] = jar_item
        for key, item in analyze_dict.items():
            if item.get('name'):
                continue
            name, version = decode_node_id(key)
            jar_analyze_item = jar_analyze_dict.get(f"{name}-{version}")
            if jar_analyze_item:
                item['name'] = jar_analyze_item.get('result', {}).get('name')
                with open(jar_analyze_item.get("path"), "r") as license_file:
                    item['data'] = license_file.read()
                    

def unzip_maven_dependencies(directory: str):
    for f in os.listdir(directory):
        if f.endswith('.jar'):
            with ZipFile(os.path.join(directory, f),"r") as zip_ref:
                zip_ref.extractall(os.path.join(directory, f.split('.jar')[0]))

def analyze_maven_jar_dependencies(dir_path: str):
    result = []
    with resources.path(lib, get_askalono()) as askalono_path:
        output_str = subprocess.run(
            [askalono_path, "--format", "json", "crawl", "--glob", GLOB, dir_path],
            stdout=subprocess.PIPE,
        ).stdout.decode("utf-8")
        output_lines = output_str.split("\n")
        for line in output_lines:
            try:
                result.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return result



def analyze_maven_dependencies(dir_path: str):
    result = []
    with resources.path(lib, get_askalono()) as askalono_path:
        output_str = subprocess.run(
            [askalono_path, "--format", "json", "crawl", "--glob", "*", dir_path],
            stdout=subprocess.PIPE,
        ).stdout.decode("utf-8")
        output_lines = output_str.split("\n")
        for line in output_lines:
            try:
                result.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return result


def get_maven_analyze_dict(directory: str) -> Dict:
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
                }
        return data_dict


def analyze_maven(directory: str, dep_tree: AnyNode) -> AnyNode:
    analyze_data = get_maven_analyze_dict(directory)
    get_jar_dependency_analyze(directory, analyze_data)
    return add_analyze_to_dep_tree(analyze_data, dep_tree)


def add_analyze_to_dep_tree(analyze_dict: Dict, dep_tree: AnyNode):
    for node in PreOrderIter(dep_tree):
        node_analyze = analyze_dict.get(node.id)
        if node_analyze:
            if node_analyze.get("name"):
                node.license_text = node_analyze.get("data")
                node.license_analyzed = node_analyze.get("name")
    return dep_tree


def fetch_maven_licenses(dep_data: Dict, dir_path: str):
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
