"""Persistence -- save and load graphs to/from JSON files.

Think of persistence like saving a video game. When you're done
playing, you save your progress to a file. Next time you start
the game, you load that file and pick up exactly where you left off.

Our graph database works the same way: you can save your entire
graph (all nodes and edges) to a JSON file, and later load it
back into memory to continue working with it.

JSON is a text format that both humans and computers can read --
it looks like a nicely organized list with curly braces and colons.

Example:
    >>> from pygraphdb.graph import Graph
    >>> from pygraphdb.persistence import save_graph, load_graph
    >>> g = Graph()
    >>> g.add_node("alice", label="Person")
    >>> save_graph(g, "/tmp/my_graph.json")
    >>> g2 = load_graph("/tmp/my_graph.json")
    >>> g2.get_node("alice").label
    'Person'

"""

import json
from pathlib import Path
from typing import cast

from pygraphdb.atomic import atomic_write_text
from pygraphdb.errors import PersistenceError
from pygraphdb.graph import Graph

# Every real save file has these top-level keys; anything else isn't one of ours.
_REQUIRED_KEYS = frozenset({"nodes", "edges"})


def save_graph(graph: Graph, file_path: str | Path) -> None:
    """Save a graph to a JSON file.

    Like saving your game progress -- writes all nodes and edges
    to a file so you can load them later.

    Args:
        graph: The graph to save.
        file_path: The path to write the JSON file to.

    """
    path = Path(file_path)
    data = graph.to_dict()
    atomic_write_text(path, json.dumps(data, indent=2, default=str))


def load_graph(file_path: str | Path) -> Graph:
    """Load a graph from a JSON file.

    Like loading a saved game -- reads nodes and edges from a file
    and rebuilds the graph in memory.

    Args:
        file_path: The path to read the JSON file from.

    Returns:
        A new Graph populated with the saved data.

    Raises:
        PersistenceError: If the file is missing, unreadable, not valid JSON,
            or not a valid save file.

    """
    path = Path(file_path)
    try:
        data: object = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        msg = f"Could not read {path}: {exc}"
        raise PersistenceError(msg) from exc
    except json.JSONDecodeError as exc:
        msg = f"Invalid JSON in {path}: {exc}"
        raise PersistenceError(msg) from exc
    if not isinstance(data, dict):
        msg = f"{path} is not a valid save file: the top level must be an object"
        raise PersistenceError(msg)
    saved: dict[str, object] = {str(k): v for k, v in cast("dict[object, object]", data).items()}
    missing = _REQUIRED_KEYS - saved.keys()
    if missing:
        msg = f"{path} is not a valid save file: missing {sorted(missing)}"
        raise PersistenceError(msg)
    try:
        return Graph.from_dict(saved)
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        msg = f"{path} is not a valid save file: {exc}"
        raise PersistenceError(msg) from exc


def graph_to_json(graph: Graph) -> str:
    """Serialize a graph to a JSON string (without writing to disk).

    Args:
        graph: The graph to serialize.

    Returns:
        A JSON string representation of the graph.

    """
    return json.dumps(graph.to_dict(), indent=2, default=str)


def graph_from_json(json_string: str) -> Graph:
    """Deserialize a graph from a JSON string.

    Args:
        json_string: A JSON string representing a graph.

    Returns:
        A new Graph populated from the JSON data.

    """
    data: dict[str, object] = json.loads(json_string)
    return Graph.from_dict(data)
