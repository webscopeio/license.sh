import unittest
import subprocess
import sys
from unittest import mock
from license_sh.helpers import get_node_id
from license_sh.analyze.analyze_shared import (
    add_analyze_to_dep_tree,
    run_askalono,
    GIT_IGNORE,
    GIT_IGNORE_DISABLED,
    get_node_analyze_dict,
)
from anytree import AnyNode, PreOrderIter


class Askalono_result:
    stdout = """{"path":"../license-sh/node_modules/snapsvg/LICENSE","result":{"score":0.9993655,"license":{"name":"Apache-2.0"}}}
{"path":"../license-sh/node_modules/react/LICENSE","result":{"score":0.9993655,"license":{"name":"Apache-2.0"}}}
{"path":"../license-sh/node_modules/redux/LICENSE","result":{"score":0.9993655,"license":{"name":"Apache-2.0"}}}""".encode()


class AnalyzeSharedTestCase(unittest.TestCase):
    def test_add_analyze_to_dep_tree_simple(self):
        tree = AnyNode(
            id="root",
            children=[
                AnyNode(id="child", children=[AnyNode(id="childChild")]),
                AnyNode(id="child2", children=[AnyNode(id="child2Child")]),
            ],
        )
        analyze = {
            "root": {"data": "Hey! I am a license text", "name": "Awesome license"},
            "childChild": {
                "data": "Hmm, i am a license text too",
                "name": "Hmm license",
            },
        }
        updated_tree = add_analyze_to_dep_tree(analyze, tree)
        self.assertEqual(updated_tree.license_text, analyze.get("root").get("data"))
        self.assertEqual(updated_tree.license_analyzed, analyze.get("root").get("name"))
        self.assertEqual(
            updated_tree.children[0].children[0].license_text,
            analyze.get("childChild").get("data"),
        )
        self.assertEqual(
            updated_tree.children[0].children[0].license_analyzed,
            analyze.get("childChild").get("name"),
        )

    def test_add_analyze_to_dep_tree_license_file_negative(self):
        tree = AnyNode(id="root")
        analyze = {
            "root": {
                "data": "Hey! I am a random text that might be license text",
                "file": "README",
            }
        }
        updated_tree = add_analyze_to_dep_tree(analyze, tree)
        try:
            self.assertEqual(updated_tree.license_text, analyze.get("root").get("data"))
            self.assertEqual(
                updated_tree.license_analyzed, analyze.get("root").get("name")
            )
        except Exception:
            pass

    def test_add_analyze_to_dep_tree_license_file_positive(self):
        tree = AnyNode(id="root")
        analyze = {
            "root": {
                "data": "Hey! I am a random text that might be license text",
                "file": "LICENSE",
            }
        }
        updated_tree = add_analyze_to_dep_tree(analyze, tree)
        self.assertEqual(updated_tree.license_text, analyze.get("root").get("data"))

    @mock.patch("license_sh.analyze.analyze_shared.subprocess")
    def test_run_askalono_simple(self, mock_subprocess):
        mock_subprocess.run.return_value = Askalono_result()
        result = run_askalono("shouldnt/matter")
        self.assertEqual(len(result), 3)
        self.assertEqual(
            result[0].get("result").get("license").get("name"), "Apache-2.0"
        )

    @mock.patch("license_sh.analyze.analyze_shared.subprocess")
    @mock.patch("os.path.isfile")
    @mock.patch("os.rename")
    def test_run_askalono_gitignore(self, mock_rename, mock_isfile, mock_subprocess):
        mock_isfile.return_value = True
        mock_subprocess.run.return_value = Askalono_result()
        result = run_askalono("shouldnt/matter")
        self.assertEqual(mock_rename.call_count, 2)

    @mock.patch("license_sh.analyze.analyze_shared.subprocess")
    @mock.patch("os.path.isfile")
    @mock.patch("os.rename")
    def test_run_askalono_gitignore_error(
        self, mock_rename, mock_isfile, mock_subprocess
    ):
        mock_isfile.return_value = True
        mock_subprocess.run.side_effect = Exception("Boom!")
        try:
            result = run_askalono("shouldnt/matter")
        except Exception:
            print("yeey")
        self.assertEqual(mock_rename.call_count, 2)

    @mock.patch("builtins.open")
    @mock.patch("json.load")
    @mock.patch("license_sh.analyze.analyze_shared.subprocess")
    def test_get_node_analyze_dict(self, mock_subprocess, mock_json_load, mock_open):
        mock_subprocess.run.return_value = Askalono_result()
        project_name = "project_name"
        project_version = "project_version"
        mock_json_load.return_value = {"name": project_name, "version": project_version}
        result = get_node_analyze_dict("shouldnt/matter")
        self.assertEqual(
            result.get(get_node_id(project_name, project_version)).get("name"),
            "Apache-2.0",
        )
        self.assertEqual(
            result.get(get_node_id(project_name, project_version)).get("file"),
            "LICENSE",
        )


if __name__ == "__main__":
    unittest.main()
