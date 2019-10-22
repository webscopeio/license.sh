# Contribution guide

This documents guides you on how to contribute to this project.

## Prerequisites

1. `git clone git@github.com:webscopeio/license.sh.git` 
2. Install 
   - [pipenv](https://github.com/pypa/pipenv)
   - [docsify](https://docsify.js.org/#/quickstart) Optionally, if you
     want to do a change in a documentation
3. `pipenv install` && `pipenv shell`
4. Run 
   - license audit of license.sh `pipenv run ./license.sh` or
   - unit tests `pipenv run python -m unittest`
   - run style formater `black .`
   - open documentation with `docsify serve ./docs`
3. Read [Architecture](architecture.md) section.

## Packaging

In order to distribute & test this package, run `python3 setup.py sdist` in a home
directory.

It will generate `.tar.gz` file in `dist/` directory which you can
install with `pip install <file.tar.gz>` 

