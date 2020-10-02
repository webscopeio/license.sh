Check licenses of your software.

<p align="center">
 <img src="https://github.com/webscopeio/license.sh/blob/master/docs/img/logo.png?raw=true" />
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python build](https://github.com/webscopeio/license.sh/workflows/Python%20build/badge.svg)
![License.sh check](https://img.shields.io/endpoint?label=license-sh&url=https%3A%2F%2Flicense.sh%2Fapi%2Fshield%3Fowner%3Dwebscopeio%26repo%3Dlicense.sh%26repoID%3D199459794%26token_type%3Dbearer%26type%3Dgithub)


The goal of this repository is to create a simple utility that you can simply run in your repository to check compliance of your 3rd party dependencies.

https://webscopeio.github.io/license.sh/#/

License compliance tool for your software.
We're currently in **Beta phase**, please feel free to help us with providing bugreports & submitting PRs.

# Installation

1. 🐍 Install pip https://pip.pypa.io/en/stable/installing/
2. 💻 `pip install license-sh`

# Usage

Run the following command inside your repository.
```bash
license-sh
```

![Screenshot](https://github.com/webscopeio/license.sh/blob/master/docs/img/preview.gif?raw=true)

# Supported Lanaguages & Package managers

- Javascript
  - NPM
  - Yarn
- Python
  - pipenv
- Java
  - maven



# Contribution guide

Available commands:

```
pipenv run check-types
pipenv run lint
pipenv run test
```

You need to set-up a repository and install dependencies using pipenv.

```bash
# clone the repo
$ git clone git@github.com:webscopeio/license.sh.git
# install pipenv
$ pipenv install
# run the project
$ pipenv run ./license-sh <path_to_test_project>
```

## Running tests

`pipenv run python -m unittest`

## Documentation
`pipenv run mkdocs serve`  

## Packaging

Read https://packaging.python.org/tutorials/packaging-projects/

1. Run `python3 setup.py sdist bdist_wheel`.
2) It will generate `.tar.gz` file in `dist/` directory which you can
3) install with `pip install <file.tar.gz>` 
