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
  -p --project <project_type>         Run only specific project [yarn | npm | maven | pipenv]
  --dependencies                      Include dependency license text analysis. Suported: npm, yarn, maven
  -i --interactive                    Runs program in an interactive mode, allows you to configure licenses and packages
  -c --config <config_path>           Use custom path to config       
  --version                           Show version.
```

## Prerequisites

Depends on the project you want to test.

!!! Prerequisites
    - Yarn - `yarn` and `node`
    - Maven - `maven` and `java`
    - Pipenv - `python`
    - Npm - `npm`

## Configuration

Stored inside `.license-sh.json` in the root of the project.

Generate interactively with `license-sh config` command.

Example:
```
{
  "ignored_packages": {
    "python_pipenv": [ 
      "PyInquirer==1.0.0",
      "setuptools==3.4.5"
    ],
    "npm": [],
    "maven": [],
    "yarn": []
  },
  "whitelist": [
    "MIT"
  ]
```

* ### Ignore packages
```
  "ignored_packages": {
    "python_pipenv": [
      "PyInquirer==1.0.0",
      "setuptools==3.4.5"
    ],
    "npm": [],
    "maven": [],
    "yarn": []
  }
```
You can ignore specific packages if it's license is unknown or you have some reason hat you don't what to see it as an error.

Format:
"{PACKAGE_NAME}:-:{PACKAGE_VESION}"  --- To ignore specific version of the package RECOMENDED 

"{PACKAGE_NAME}" --- To ignore every version of this specific package


* ### Whitelist
```
  "whitelist": [
    "MIT"
  ]
```
Whitelist is a list of green licenses that shouldn't throw an error if found.
