# Configuration

Configuration is stored inside `.license-sh.json` in the root of the project.

It can be generated interactively with `license-sh config` command or modified when running with `-i, --interactivity` 
flag.

Example:
```
{
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

## Ignored packages
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

## Whitelisted licenses
```
  "whitelist": [
    "MIT"
  ]
```
Whitelist is a list of green licenses that shouldn't throw an error if found.
