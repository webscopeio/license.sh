<p align="center">
 <img src="https://github.com/webscopeio/license.sh/blob/master/docs/img/logo.png?raw=true" />
</p>

The goal of this repository is to create a simple utility that you can simply run in your repository to check compliance of your 3rd party dependencies.

https://webscopeio.github.io/license.sh/#/

License compliance tool for your software.
We're currently in **Beta phase**, please feel free to help us with providing bugreports & submitting PRs.


# Usage

Run the following command inside your repository.
```bash
license-sh
```

![Screenshot](https://github.com/webscopeio/license.sh/blob/master/docs/img/screenshot.png?raw=true)

# Supported Lanaguages & Package managers

- Javascript
  - NPM
  - Yarn
- Python
  - pipenv
- Java
  - maven



# Contribution guide

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
`docsify serve ./docs`  

## Packaging

Read https://packaging.python.org/tutorials/packaging-projects/

1. Run `python3 setup.py sdist bdist_wheel`.
2) It will generate `.tar.gz` file in `dist/` directory which you can
3) install with `pip install <file.tar.gz>` 
