# Usage

## Basic Usage

```
License.sh

Usage:
  license-sh config
  license-sh [options]
  license-sh <path> [options]
  license-sh (-h | --help)
  license-sh --version

Options:
  -h --help                           Show this screen.
  -o <reporter> --output <reporter>   Output [default: console].
  -t --tree                           Show full dependency tree.
  -d --debug                          Debug mode
  --version                           Show version.
```

## Configuration

Stored inside `.license-sh.json` in the root of the project.

Generate interactively with `license-sh config` command.

Example:
```
{
  "projects": [
    {
      "directory": ".",
      "type": "python_pipenv"
    }
  ],
  "whitelist": [
    "MIT"
  ]
```
