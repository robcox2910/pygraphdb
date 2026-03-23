"""Test BFS and DFS traversal algorithms."""

import pytest

from pygraphdb.errors import NodeNotFoundError
from pygraphdb.graph import Graph
from pygraphdb.traversal import bfs, dfs

THREE_NODES = 3
FOUR_NODES = 4
ONE_NODE = 1


def _build_chain() -> Graph:
    """Build a linear chain: a -> b -> c -> d."""
    g = Graph()
    for nid in ("a", "b", "c", "d"):
        g.add_node(nid)
    g.add_edge("e1", "a", "b")
    g.add_edge("e2", "b", "c")
    g.add_edge("e3", "c", "d")
    return g


def _build_diamond() -> Graph:
    """Build a diamond: a -> b, a -> c, b -> d, c -> d."""
    g = Graph()
    for nid in ("a", "b", "c", "d"):
        g.add_node(nid)
    g.add_edge("e1", "a", "b")
    g.add_edge("e2", "a", "c")
    g.add_edge("e3", "b", "d")
    g.add_edge("e4", "c", "d")
    return g


class TestBfs:
    """Test breadth-first search."""

    def test_bfs_chain(self) -> None:
        """BFS on a chain visits nodes in order."""
        g = _build_chain()
        result = bfs(g, "a")
        ids = [n.node_id for n in result]
        assert ids == ["a", "b", "c", "d"]

    def test_bfs_diamond(self) -> None:
        """BFS on a diamond visits all reachable nodes."""
        g = _build_diamond()
        result = bfs(g, "a")
        assert len(result) == FOUR_NODES
        # 'a' is first, 'd' is last
        assert result[0].node_id == "a"
        assert result[-1].node_id == "d"

    def test_bfs_single_node(self) -> None:
        """BFS from a node with no edges returns just that node."""
        g = Graph()
        g.add_node("lonely")
        result = bfs(g, "lonely")
        assert len(result) == ONE_NODE
        assert result[0].node_id == "lonely"

    def test_bfs_missing_start_raises(self) -> None:
        """BFS from a non-existent node raises NodeNotFoundError."""
        g = Graph()
        with pytest.raises(NodeNotFoundError):
            bfs(g, "missing")

    def test_bfs_partial_graph(self) -> None:
        """BFS only visits reachable nodes."""
        g = Graph()
        g.add_node("a")
        g.add_node("b")
        g.add_node("island")
        g.add_edge("e1", "a", "b")
        result = bfs(g, "a")
        ids = {n.node_id for n in result}
        assert "island" not in ids


class TestDfs:
    """Test depth-first search."""

    def test_dfs_chain(self) -> None:
        """DFS on a chain visits nodes in order."""
        g = _build_chain()
        result = dfs(g, "a")
        ids = [n.node_id for n in result]
        assert ids == ["a", "b", "c", "d"]

    def test_dfs_diamond(self) -> None:
        """DFS on a diamond visits all reachable nodes."""
        g = _build_diamond()
        result = dfs(g, "a")
        assert len(result) == FOUR_NODES
        assert result[0].node_id == "a"

    def test_dfs_single_node(self) -> None:
        """DFS from a node with no edges returns just that node."""
        g = Graph()
        g.add_node("lonely")
        result = dfs(g, "lonely")
        assert len(result) == ONE_NODE

    def test_dfs_missing_start_raises(self) -> None:
        """DFS from a non-existent node raises NodeNotFoundError."""
        g = Graph()
        with pytest.raises(NodeNotFoundError):
            dfs(g, "missing")

    def test_dfs_no_revisits(self) -> None:
        """DFS never visits the same node twice (cycle handling)."""
        g = Graph()
        g.add_node("a")
        g.add_node("b")
        g.add_edge("e1", "a", "b")
        g.add_edge("e2", "b", "a")  # cycle
        result = dfs(g, "a")
        ids = [n.node_id for n in result]
        assert len(ids) == len(set(ids))
