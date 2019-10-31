![License.sh logo](https://license-sh.now.sh/static/images/license-logo-dark.png)

License compliance tool for your software

# Usage

Run the following command inside your repository.
```bash
license-sh
```



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

Run `python3 setup.py sdist`.
It will generate `.tar.gz` file in `dist/` directory which you can
install with `pip install <file.tar.gz>` 
