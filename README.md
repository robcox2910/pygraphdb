# PyGraphDB

An educational graph database library built from scratch in Python. Part of the **PyLearn** educational platform for kids aged 12+.

A graph database stores data as **nodes** (entities) and **edges** (relationships) -- like a social network map where people are dots and friendships are lines connecting them.

## Features

- **Nodes & Edges** -- Create entities with labels and properties, connect them with typed relationships
- **CRUD Operations** -- Add, get, update, and delete nodes and edges
- **Graph Traversal** -- Explore your graph with BFS (breadth-first) and DFS (depth-first) algorithms
- **Shortest Path** -- Find the quickest route between two nodes (like GPS directions)
- **Pattern Matching** -- Search for nodes and edges by label, type, or properties
- **Cypher-like Queries** -- Ask questions with a simple query language inspired by Neo4j's Cypher
- **Persistence** -- Save and load your graph to/from JSON files
- **Neighbor & Degree** -- Find connected nodes and count connections

## Quick Start

```python
from pygraphdb import Graph, bfs, shortest_path, execute_query, find_nodes

# Create a social network
g = Graph()
g.add_node("alice", label="Person", properties={"name": "Alice", "age": 13})
g.add_node("bob", label="Person", properties={"name": "Bob", "age": 14})
g.add_node("charlie", label="Person", properties={"name": "Charlie", "age": 13})

g.add_edge("e1", "alice", "bob", rel_type="KNOWS")
g.add_edge("e2", "bob", "charlie", rel_type="KNOWS")

# Find Alice's friends
friends = g.get_neighbors("alice", direction="outgoing")
print([f.properties["name"] for f in friends])  # ['Bob']

# Traverse the whole network
visited = bfs(g, "alice")
print([n.properties["name"] for n in visited])  # ['Alice', 'Bob', 'Charlie']

# Find shortest path
path = shortest_path(g, "alice", "charlie")
print([n.properties["name"] for n in path])  # ['Alice', 'Bob', 'Charlie']

# Query with Cypher-like syntax
results = execute_query(g, 'MATCH (n:Person) WHERE n.name = "Alice" RETURN n')
print(results[0].properties["name"])  # 'Alice'

# Pattern matching
teenagers = find_nodes(g, label="Person")
print(len(teenagers))  # 3
```

## Installation

```bash
# Clone and install
git clone https://github.com/robcox2910/pygraphdb.git
cd pygraphdb
uv sync --all-extras

# Run tests
uv run pytest

# Lint & type check
uv run ruff check src/ tests/
uv run pyright src tests
```

## Releasing

Other projects in the series ([PyStack](https://github.com/robcox2910/pystack)) use a released version of this one from PyPI,
not whatever is on `main`. To publish a change for them:

1. Merge the change to `main`.
2. Release it: `gh release create vX.Y.Z --target main --generate-notes`
   (or push a `vX.Y.Z` tag); the release workflow publishes it to PyPI.
   A change to the public API bumps the minor version (`v0.1.0` → `v0.2.0`);
   anything else bumps the patch (`v0.1.0` → `v0.1.1`).
3. In each project that uses it, raise the `fromscratch-pygraphdb>=X.Y.Z` floor in
   `pyproject.toml`, run `uv lock --upgrade-package fromscratch-pygraphdb`, and open
   a pull request so CI checks the pair together.

<!-- series:start -->
## Related Projects

This project is one of a series that builds real systems "from scratch in Python" to teach how they work. See the [series home](https://robcox2910.github.io/) for the full story.

| Project | What it teaches | Repository | Docs | PyPI |
| --- | --- | --- | --- | --- |
| PyOS | Operating systems | [py-os](https://github.com/robcox2910/py-os) | [Docs](https://robcox2910.github.io/py-os/) | [fromscratch-pyos](https://pypi.org/project/fromscratch-pyos/) |
| Pebble | Compilers and programming languages | [pebble-lang](https://github.com/robcox2910/pebble-lang) | [Docs](https://robcox2910.github.io/pebble-lang/) | [fromscratch-pebble](https://pypi.org/project/fromscratch-pebble/) |
| PyDB | Relational databases | [pydb](https://github.com/robcox2910/pydb) | [Docs](https://robcox2910.github.io/pydb/) | [fromscratch-pydb](https://pypi.org/project/fromscratch-pydb/) |
| PyKV | Key-value stores | [pykv](https://github.com/robcox2910/pykv) | [Docs](https://robcox2910.github.io/pykv/) | [fromscratch-pykv](https://pypi.org/project/fromscratch-pykv/) |
| PyDocDB | Document databases | [pydoc-db](https://github.com/robcox2910/pydoc-db) | [Docs](https://robcox2910.github.io/pydoc-db/) | [fromscratch-pydocdb](https://pypi.org/project/fromscratch-pydocdb/) |
| **PyGraphDB** | **Graph databases** | [pygraphdb](https://github.com/robcox2910/pygraphdb) | [Docs](https://robcox2910.github.io/pygraphdb/) | [fromscratch-pygraphdb](https://pypi.org/project/fromscratch-pygraphdb/) |
| PyTSDB | Time-series databases | [pytsdb](https://github.com/robcox2910/pytsdb) | [Docs](https://robcox2910.github.io/pytsdb/) | [fromscratch-pytsdb](https://pypi.org/project/fromscratch-pytsdb/) |
| PyVecDB | Vector databases | [pyvecdb](https://github.com/robcox2910/pyvecdb) | [Docs](https://robcox2910.github.io/pyvecdb/) | [fromscratch-pyvecdb](https://pypi.org/project/fromscratch-pyvecdb/) |
| PyColDB | Column-family databases | [pycoldb](https://github.com/robcox2910/pycoldb) | [Docs](https://robcox2910.github.io/pycoldb/) | [fromscratch-pycoldb](https://pypi.org/project/fromscratch-pycoldb/) |
| PyCrypt | Cryptography | [pycrypt](https://github.com/robcox2910/pycrypt) | [Docs](https://robcox2910.github.io/pycrypt/) | [fromscratch-pycrypt](https://pypi.org/project/fromscratch-pycrypt/) |
| PyNet | Computer networking | [pynet](https://github.com/robcox2910/pynet) | [Docs](https://robcox2910.github.io/pynet/) | [fromscratch-pynet](https://pypi.org/project/fromscratch-pynet/) |
| PyWeb | HTTP web servers | [pyweb](https://github.com/robcox2910/pyweb) | [Docs](https://robcox2910.github.io/pyweb/) | [fromscratch-pyweb](https://pypi.org/project/fromscratch-pyweb/) |
| PyGit | Version control | [pygit](https://github.com/robcox2910/pygit) | [Docs](https://robcox2910.github.io/pygit/) | [fromscratch-pygit](https://pypi.org/project/fromscratch-pygit/) |
| PySearch | Search engines | [pysearch](https://github.com/robcox2910/pysearch) | [Docs](https://robcox2910.github.io/pysearch/) | [fromscratch-pysearch](https://pypi.org/project/fromscratch-pysearch/) |
| PyMQ | Message queues | [pymq](https://github.com/robcox2910/pymq) | [Docs](https://robcox2910.github.io/pymq/) | [fromscratch-pymq](https://pypi.org/project/fromscratch-pymq/) |
| PyLLM | Language models (the brain) | [pyllm](https://github.com/robcox2910/pyllm) | [Docs](https://robcox2910.github.io/pyllm/) | [fromscratch-pyllm](https://pypi.org/project/fromscratch-pyllm/) |
| PyScheduler | Job scheduling | [pyscheduler](https://github.com/robcox2910/pyscheduler) | [Docs](https://robcox2910.github.io/pyscheduler/) | [fromscratch-pyscheduler](https://pypi.org/project/fromscratch-pyscheduler/) |
| PyStack | Full-stack integration | [pystack](https://github.com/robcox2910/pystack) | [Docs](https://robcox2910.github.io/pystack/) | [fromscratch-pystack](https://pypi.org/project/fromscratch-pystack/) |
<!-- series:end -->

<!-- docs:start -->
## Documentation

Full docs (with kid-friendly explanations of every idea): https://robcox2910.github.io/pygraphdb/

## Install

[![PyPI](https://img.shields.io/pypi/v/fromscratch-pygraphdb)](https://pypi.org/project/fromscratch-pygraphdb/)

```bash
pip install fromscratch-pygraphdb
```

Or get the whole series at once: `pip install fromscratch-pystack`.
<!-- docs:end -->
