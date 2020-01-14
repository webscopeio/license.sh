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
  "ignored_packages": {
    "python_pipenv": [
      "PyInquirer",
      "setuptools"
    ],
    "npm": [],
    "maven": [],
    "yarn": []
  },
  "whitelist": [
    "MIT"
  ]
```
* ### Projects
```
  "projects": [
    {
      "directory": ".",
      "type": "python_pipenv"
    }
  ],
```
Projects property is use to set paths and types of the projects. This can be dynamically generated.

* ### Ignore packages
```
  "ignored_packages": {
    "python_pipenv": [
      "PyInquirer",
      "setuptools"
    ],
    "npm": [],
    "maven": [],
    "yarn": []
  }
```
You can ignore specific packages if it's license is unknown or you have some reason hat you don't what to see it as an error

* ### Whitelist
```
  "whitelist": [
    "MIT"
  ]
```
Whitelist is a list of green licenses that shouldn't throw an error if found.
