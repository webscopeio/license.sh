import unittest
from unittest import mock
from unittest.mock import mock_open

from anytree import AnyNode

from license_sh.analyze.pipenv import get_pipenv_analyze_dict, analyze_pipenv

ANALYZE_RESULT = [
    {
        "path": "../target/dependencies/react-15.5.4.dist-info/LICENSE",
        "result": {"score": 0.9993655, "license": {"name": "Apache-2.0"}},
    },
    {
        "path": "../target/dependencies/react-15.5.4.dist-info/LICENSE-MIT",
        "result": {"score": 0.9993655, "license": {"name": "MIT"}},
    },
    {
        "path": "../target/dependencies/redux-4.4.4-GA.dist-info/LICENSE",
        "result": {"score": 0.9993655, "license": {"name": "Apache-2.0"}},
    },
    {
        "path": "../target/dependencies/package-5.5.5.dist-info/LICENSE",
        "error": "Error message",
    },
]


class AnalyzePipenvTestCase(unittest.TestCase):
    @mock.patch("builtins.open", callable=mock_open(read_data="data"))
    @mock.patch(
        "license_sh.analyze.pipenv.get_analyze_pipenv_data", return_value=ANALYZE_RESULT
    )
    def test_get_pipenv_analyze_dict(self, mock_analyze_data, mock_open):
        result = get_pipenv_analyze_dict("doenst/matter")
        self.assertEqual(result.get("react-15.5.4")[0].get("name"), "Apache-2.0")
        self.assertEqual(result.get("react-15.5.4")[1].get("name"), "MIT")
        self.assertEqual(result.get("redux-4.4.4-GA")[0].get("name"), "Apache-2.0")

    @mock.patch(
        "license_sh.analyze.pipenv.get_pipenv_analyze_dict",
        return_value={
            "react-15.5.4": [
                {"data": "License text", "name": "MIT", "file": "LICENSE"},
                {"data": "License text", "name": "Apache-2.0", "file": "LICENSE"},
            ],
            "redux-15.5.4": [{"data": "README text", "name": None, "file": "README"}],
        },
    )
    def test_analyze_pipenv(self, mock_get_pipenv_analyze_dict):
        tree = AnyNode(
            name="root",
            version="1.0.0",
            children=[
                AnyNode(name="react", version="15.5.4"),
                AnyNode(name="redux", version="15.5.4"),
            ],
        )
        # TODO - make this immutable
        analyze_pipenv("doesnt/matter", tree)
        self.assertEqual(
            tree.children[0].analyze,
            [
                {"data": "License text", "name": "MIT"},
                {"data": "License text", "name": "Apache-2.0"},
            ],
        )
        self.assertEqual(
            tree.children[1].analyze, [],
        )
