"""Test shortest path and all-paths algorithms."""

import pytest

from pygraphdb.errors import NodeNotFoundError
from pygraphdb.graph import Graph
from pygraphdb.pathfinding import all_paths, shortest_path

ONE_NODE = 1
TWO_PATHS = 2
THREE_NODES = 3
FOUR_NODES = 4


def _build_diamond() -> Graph:
    """Build a diamond: a -> b -> d, a -> c -> d."""
    g = Graph()
    for nid in ("a", "b", "c", "d"):
        g.add_node(nid)
    g.add_edge("e1", "a", "b")
    g.add_edge("e2", "a", "c")
    g.add_edge("e3", "b", "d")
    g.add_edge("e4", "c", "d")
    return g


class TestShortestPath:
    """Test BFS-based shortest path finding."""

    def test_shortest_path_direct(self) -> None:
        """Find shortest path with a direct connection."""
        g = Graph()
        g.add_node("a")
        g.add_node("b")
        g.add_edge("e1", "a", "b")
        path = shortest_path(g, "a", "b")
        ids = [n.node_id for n in path]
        assert ids == ["a", "b"]

    def test_shortest_path_through_chain(self) -> None:
        """Find shortest path through a chain."""
        g = Graph()
        for nid in ("a", "b", "c"):
            g.add_node(nid)
        g.add_edge("e1", "a", "b")
        g.add_edge("e2", "b", "c")
        path = shortest_path(g, "a", "c")
        ids = [n.node_id for n in path]
        assert ids == ["a", "b", "c"]

    def test_shortest_path_diamond(self) -> None:
        """Shortest path in a diamond has 3 nodes (skips one branch)."""
        g = _build_diamond()
        path = shortest_path(g, "a", "d")
        assert len(path) == THREE_NODES
        assert path[0].node_id == "a"
        assert path[-1].node_id == "d"

    def test_shortest_path_same_node(self) -> None:
        """Shortest path from a node to itself is just that node."""
        g = Graph()
        g.add_node("a")
        path = shortest_path(g, "a", "a")
        assert len(path) == ONE_NODE
        assert path[0].node_id == "a"

    def test_shortest_path_no_path(self) -> None:
        """Return empty list when no path exists."""
        g = Graph()
        g.add_node("a")
        g.add_node("b")
        path = shortest_path(g, "a", "b")
        assert path == []

    def test_shortest_path_missing_node_raises(self) -> None:
        """Shortest path with a missing node raises NodeNotFoundError."""
        g = Graph()
        g.add_node("a")
        with pytest.raises(NodeNotFoundError):
            shortest_path(g, "a", "missing")


class TestAllPaths:
    """Test finding all paths between two nodes."""

    def test_all_paths_diamond(self) -> None:
        """Find both paths through a diamond."""
        g = _build_diamond()
        paths = all_paths(g, "a", "d")
        assert len(paths) == TWO_PATHS
        for path in paths:
            assert path[0].node_id == "a"
            assert path[-1].node_id == "d"

    def test_all_paths_no_path(self) -> None:
        """Return empty list when no path exists."""
        g = Graph()
        g.add_node("a")
        g.add_node("b")
        paths = all_paths(g, "a", "b")
        assert paths == []

    def test_all_paths_same_node(self) -> None:
        """All paths from a node to itself returns a single path."""
        g = Graph()
        g.add_node("a")
        paths = all_paths(g, "a", "a")
        assert len(paths) == ONE_NODE
        assert paths[0][0].node_id == "a"

    def test_all_paths_respects_max_depth(self) -> None:
        """Respect the max_depth limit."""
        g = Graph()
        for nid in ("a", "b", "c", "d"):
            g.add_node(nid)
        g.add_edge("e1", "a", "b")
        g.add_edge("e2", "b", "c")
        g.add_edge("e3", "c", "d")
        # max_depth=1 means only 1-hop paths
        paths = all_paths(g, "a", "d", max_depth=1)
        assert paths == []

    def test_all_paths_missing_node_raises(self) -> None:
        """All paths with a missing node raises NodeNotFoundError."""
        g = Graph()
        with pytest.raises(NodeNotFoundError):
            all_paths(g, "missing", "also_missing")
