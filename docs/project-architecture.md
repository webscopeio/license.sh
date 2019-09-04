# Architecture

This document describes an architecture of this software.

It's written in Python and uses `pipenv` as a package manager.


## Main Components
The architecture consists of 4 main components:

1. **Project identification** - First, we need to identify the type of project in a directory. Basically, `license.sh` need to know what kind of runner it should use for your project.
It could use NpmRunner, Python runner etc.
2. **Runners** - Runners are the :green_heart: of the application, they
   transitively identify all of the project dependencies and their
   licenses. The output of a runner is a [License Dependency Tree](#license-dependency-tree).
3. **License analysis** - `TODO`
4. **Reporters** - Take the input from the runner and output it in various formats.

In the following sections, we will describe each of these components in more detail.

### Project Identification

Project identification is implemented in a simple function which returns
an array of project types. We return an array of types, because there
can be multiple projects types in a single directory e.g. `Pipfile` &
`package.json` next to each other.
```python
def get_project_types() -> [ProjectType]:
  ...
 ```
 

### License analysis

License analysis is a process of identifying whether a particular
license is in compliance with a current settings optionally defined in
`.license-sh.json5` file.

#### License normalization

### Runners

### Reporters


## Data structures

There are two main data structures that are used in this project.:w 

1. License Dependency tree
2. Bad Subtrees Array

We will now describe them in more detail.

### License Dependency tree

This tree is a completely resolved and expanded dependency tree of an
application. Node of this tree looks like this:

```json
{
  "name": "package_name",
  "version": "1.0.0",
  "license": "MIT",
  "children": [
    {
      "name": "package_name_2",
      "version": "1.0.1",
      "license": "Uknown",
      "children": [
        ...
      ]
    },
    ...
  ]
}
```

It's constructed by each resolver based on package manager metadata e.g.
`package-lock.json`, `Pipfile.lock`. Licenses are fetched by a resolved 
from central repositories e.g. NPM or PyPI.

### Annotated License Dependency tree

The complete dependency tree is usually not what user wants to see as a
result of his/her analysis. 

What is interesting for an user is to identify which one of the root
dependencies is not in allowed licenses and see all problematic paths
for that dependency.

Annotated License Dependency tree is an extension of a
[License Dependency Tree](#license-dependency-tree). 

Each node has two more properties:

1. `licenseProblem`: `boolean` - identifies whether this specific node's
   license is problematic within the current whitelist.
2. `subtreeProblem`: `boolean` - helps to identify whether this node has
   a problem within it's own sub dependencies. Reporters use this
   property in order to show / hide children. They usually don't show
   them by default if everything is fine and the this property is
   `False`.
 
