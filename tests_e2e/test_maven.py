import unittest

from license_sh.commands.run_license_sh import run_license_sh
from anytree.importer import JsonImporter
from unittest.mock import patch
from tests_e2e import test_data
from importlib import resources

ARGUMENTS = {
    '--config': None,
    '--debug': False,
    '--dependencies': False,
    '--help': False,
    '--interactive': False,
    '--output': 'console',
    '--project': None,
    '--tree': False,
    '--version': False,
    '<path>': None,
    'config': False
}


class MavenCase(unittest.TestCase):
    @patch('builtins.print')
    def test_valid_json(self, print_mock):
        with resources.path(test_data, "") as test_data_path:
            with self.assertRaises(SystemExit):
                run_license_sh({**ARGUMENTS, **{
                    '--output': 'json',
                    '<path>': test_data_path,
                    '--project': 'maven'
                }})
        calls = print_mock.call_args_list

        std_out = ""
        for call in calls:
            file_arg = call.kwargs.get('file', None)
            if not file_arg:
                std_out += ''.join(call.args)
        self.assertTrue(bool(JsonImporter().import_(std_out)))


if __name__ == '__main__':
    unittest.main()
