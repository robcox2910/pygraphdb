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

Other projects in the series ([PyStack](https://github.com/robcox2910/pystack)) use a pinned release of this one,
not whatever is on `main`. To publish a change for them:

1. Merge the change to `main`.
2. Tag it: `git tag -a vX.Y.Z -m vX.Y.Z && git push origin vX.Y.Z`.
   A change to the public API bumps the minor version (`v0.1.0` → `v0.2.0`);
   anything else bumps the patch (`v0.1.0` → `v0.1.1`).
3. In each project that uses it, edit the tag in `[tool.uv.sources]`, run
   `uv lock --upgrade-package <name>`, and open a pull request so CI checks
   the pair together.

## Related Projects

| Project | Description |
|---------|-------------|
| [py-os](https://github.com/robcox2910/py-os) | Educational operating system concepts |
| [pebble-lang](https://github.com/robcox2910/pebble-lang) | Educational programming language |
| [pydb](https://github.com/robcox2910/pydb) | Educational relational database engine |
| [pyweb](https://github.com/robcox2910/pyweb) | Educational web framework |
| [pygit](https://github.com/robcox2910/pygit) | Educational version control system |
| [pycrypt](https://github.com/robcox2910/pycrypt) | Educational cryptography library |
| [pynet](https://github.com/robcox2910/pynet) | Educational networking library |
| [pysearch](https://github.com/robcox2910/pysearch) | Educational search engine |
| [pymq](https://github.com/robcox2910/pymq) | Educational message queue |
| [pykv](https://github.com/robcox2910/pykv) | Educational key-value store |
| [pydoc-db](https://github.com/robcox2910/pydoc-db) | Educational document database |
| [pystack](https://github.com/robcox2910/pystack) | Unified platform integrating all projects |
