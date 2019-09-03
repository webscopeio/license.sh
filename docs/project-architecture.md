# Architecture

This document describes an architecture of this software.

It's written in Python and uses `pipenv` as a package manager.


## Main Components
The architecture consists of 3 main components:

1. **Project identification** - First, we need to identify the type of project in a directory. Basically, `license.sh` need to know what kind of runner it should use for your project.
It could use NpmRunner, Python runner etc.
2. **Runners** - Runners are the :green_heart: of the application, they transitively identify all of the project dependencies and their licenses.
4. **Reporters** - Take the input from the runner and output it in various formats.

In the following sections, we will describe each of these components in more detail.

### Project Identification

### Runners

### Reporters


## Data structures

There are two main data structures that are used in this project. These structures serve as a bridge between runners and reporters described above.

1. Dependency tree
2. License map

We will now describe them in more detail.

### Dependency tree

### License map
