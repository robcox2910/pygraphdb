"""PyGraphDB -- an educational graph database built from scratch in Python.

A graph database stores data as nodes (entities) and edges (relationships),
like a social network map. This library teaches you how graph databases
work by building one step by step.

Think of it like this:
- **Nodes** are people at a party
- **Edges** are the friendships between them
- **The Graph** is the party itself -- it keeps track of everyone and
  who knows whom
- **Traversal** is walking around the party visiting people
- **Queries** are questions you ask, like "Who are Alice's friends?"

Quick start:
    >>> from pygraphdb import Graph
    >>> g = Graph()
    >>> g.add_node("alice", label="Person", properties={"name": "Alice"})
    >>> g.add_node("bob", label="Person", properties={"name": "Bob"})
    >>> g.add_edge("e1", "alice", "bob", rel_type="KNOWS")
    >>> friends = g.get_neighbors("alice")
    >>> friends[0].properties["name"]
    'Bob'
"""

from pygraphdb.edge import Edge
from pygraphdb.errors import (
    DuplicateEdgeError,
    DuplicateNodeError,
    EdgeNotFoundError,
    GraphError,
    NodeNotFoundError,
    QuerySyntaxError,
)
from pygraphdb.graph import Graph
from pygraphdb.matching import find_edges, find_nodes
from pygraphdb.node import Node
from pygraphdb.pathfinding import all_paths, shortest_path
from pygraphdb.persistence import graph_from_json, graph_to_json, load_graph, save_graph
from pygraphdb.query import execute_query
from pygraphdb.traversal import bfs, dfs

__all__ = [
    "DuplicateEdgeError",
    "DuplicateNodeError",
    "Edge",
    "EdgeNotFoundError",
    "Graph",
    "GraphError",
    "Node",
    # Errors
    "NodeNotFoundError",
    "QuerySyntaxError",
    "all_paths",
    # Traversal
    "bfs",
    "dfs",
    # Query
    "execute_query",
    "find_edges",
    # Matching
    "find_nodes",
    "graph_from_json",
    "graph_to_json",
    "load_graph",
    # Persistence
    "save_graph",
    # Pathfinding
    "shortest_path",
]
