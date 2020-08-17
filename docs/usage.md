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
