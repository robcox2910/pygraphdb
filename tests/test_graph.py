"""Test the Graph container class."""

import pytest

from pygraphdb.errors import (
    DuplicateEdgeError,
    DuplicateNodeError,
    EdgeNotFoundError,
    NodeNotFoundError,
)
from pygraphdb.graph import Graph

INITIAL_COUNT = 0
ONE_NODE = 1
TWO_NODES = 2
THREE_NODES = 3
ONE_EDGE = 1
TWO_EDGES = 2


class TestGraphNodeCrud:
    """Test node CRUD operations on the Graph."""

    def test_add_node(self) -> None:
        """Add a node to the graph."""
        g = Graph()
        node = g.add_node("1", label="Person", properties={"name": "Alice"})
        assert node.node_id == "1"
        assert g.node_count == ONE_NODE

    def test_add_duplicate_node_raises(self) -> None:
        """Add a node with an existing ID raises DuplicateNodeError."""
        g = Graph()
        g.add_node("1")
        with pytest.raises(DuplicateNodeError):
            g.add_node("1")

    def test_get_node(self) -> None:
        """Get an existing node by ID."""
        g = Graph()
        g.add_node("1", label="Person")
        node = g.get_node("1")
        assert node.label == "Person"

    def test_get_missing_node_raises(self) -> None:
        """Get a non-existent node raises NodeNotFoundError."""
        g = Graph()
        with pytest.raises(NodeNotFoundError):
            g.get_node("missing")

    def test_has_node(self) -> None:
        """Check node existence."""
        g = Graph()
        g.add_node("1")
        assert g.has_node("1")
        assert not g.has_node("2")

    def test_update_node_label(self) -> None:
        """Update a node's label."""
        g = Graph()
        g.add_node("1", label="Person")
        g.update_node("1", label="Student")
        assert g.get_node("1").label == "Student"

    def test_update_node_properties(self) -> None:
        """Update a node's properties (merge)."""
        g = Graph()
        g.add_node("1", properties={"name": "Alice"})
        expected_age = 13
        g.update_node("1", properties={"age": expected_age})
        node = g.get_node("1")
        assert node.properties["name"] == "Alice"
        assert node.properties["age"] == expected_age

    def test_update_missing_node_raises(self) -> None:
        """Update a non-existent node raises NodeNotFoundError."""
        g = Graph()
        with pytest.raises(NodeNotFoundError):
            g.update_node("missing", label="X")

    def test_remove_node(self) -> None:
        """Remove a node from the graph."""
        g = Graph()
        g.add_node("1")
        removed = g.remove_node("1")
        assert removed.node_id == "1"
        assert g.node_count == INITIAL_COUNT

    def test_remove_node_removes_connected_edges(self) -> None:
        """Remove a node also removes its edges."""
        g = Graph()
        g.add_node("1")
        g.add_node("2")
        g.add_edge("e1", "1", "2")
        g.remove_node("1")
        assert g.edge_count == INITIAL_COUNT

    def test_remove_missing_node_raises(self) -> None:
        """Remove a non-existent node raises NodeNotFoundError."""
        g = Graph()
        with pytest.raises(NodeNotFoundError):
            g.remove_node("missing")

    def test_get_all_nodes(self) -> None:
        """Get all nodes returns a list of all nodes."""
        g = Graph()
        g.add_node("1")
        g.add_node("2")
        nodes = g.get_all_nodes()
        assert len(nodes) == TWO_NODES


class TestGraphEdgeCrud:
    """Test edge CRUD operations on the Graph."""

    def test_add_edge(self) -> None:
        """Add an edge between two existing nodes."""
        g = Graph()
        g.add_node("1")
        g.add_node("2")
        edge = g.add_edge("e1", "1", "2", rel_type="KNOWS")
        assert edge.edge_id == "e1"
        assert g.edge_count == ONE_EDGE

    def test_add_duplicate_edge_raises(self) -> None:
        """Add an edge with an existing ID raises DuplicateEdgeError."""
        g = Graph()
        g.add_node("1")
        g.add_node("2")
        g.add_edge("e1", "1", "2")
        with pytest.raises(DuplicateEdgeError):
            g.add_edge("e1", "1", "2")

    def test_add_edge_missing_source_raises(self) -> None:
        """Add an edge with a missing source node raises NodeNotFoundError."""
        g = Graph()
        g.add_node("2")
        with pytest.raises(NodeNotFoundError):
            g.add_edge("e1", "missing", "2")

    def test_add_edge_missing_target_raises(self) -> None:
        """Add an edge with a missing target node raises NodeNotFoundError."""
        g = Graph()
        g.add_node("1")
        with pytest.raises(NodeNotFoundError):
            g.add_edge("e1", "1", "missing")

    def test_get_edge(self) -> None:
        """Get an existing edge by ID."""
        g = Graph()
        g.add_node("1")
        g.add_node("2")
        g.add_edge("e1", "1", "2", rel_type="KNOWS")
        edge = g.get_edge("e1")
        assert edge.rel_type == "KNOWS"

    def test_get_missing_edge_raises(self) -> None:
        """Get a non-existent edge raises EdgeNotFoundError."""
        g = Graph()
        with pytest.raises(EdgeNotFoundError):
            g.get_edge("missing")

    def test_has_edge(self) -> None:
        """Check edge existence."""
        g = Graph()
        g.add_node("1")
        g.add_node("2")
        g.add_edge("e1", "1", "2")
        assert g.has_edge("e1")
        assert not g.has_edge("e2")

    def test_update_edge(self) -> None:
        """Update an edge's type and properties."""
        g = Graph()
        g.add_node("1")
        g.add_node("2")
        g.add_edge("e1", "1", "2", rel_type="KNOWS")
        g.update_edge("e1", rel_type="FRIENDS_WITH", properties={"close": True})
        edge = g.get_edge("e1")
        assert edge.rel_type == "FRIENDS_WITH"
        assert edge.properties["close"] is True

    def test_update_missing_edge_raises(self) -> None:
        """Update a non-existent edge raises EdgeNotFoundError."""
        g = Graph()
        with pytest.raises(EdgeNotFoundError):
            g.update_edge("missing", rel_type="X")

    def test_remove_edge(self) -> None:
        """Remove an edge from the graph."""
        g = Graph()
        g.add_node("1")
        g.add_node("2")
        g.add_edge("e1", "1", "2")
        removed = g.remove_edge("e1")
        assert removed.edge_id == "e1"
        assert g.edge_count == INITIAL_COUNT

    def test_remove_missing_edge_raises(self) -> None:
        """Remove a non-existent edge raises EdgeNotFoundError."""
        g = Graph()
        with pytest.raises(EdgeNotFoundError):
            g.remove_edge("missing")

    def test_get_all_edges(self) -> None:
        """Get all edges returns a list of all edges."""
        g = Graph()
        g.add_node("1")
        g.add_node("2")
        g.add_node("3")
        g.add_edge("e1", "1", "2")
        g.add_edge("e2", "2", "3")
        edges = g.get_all_edges()
        assert len(edges) == TWO_EDGES


class TestGraphNeighbors:
    """Test neighbor and degree operations."""

    def _build_triangle(self) -> Graph:
        """Build a simple triangle graph: 1->2->3, 1->3."""
        g = Graph()
        g.add_node("1")
        g.add_node("2")
        g.add_node("3")
        g.add_edge("e1", "1", "2")
        g.add_edge("e2", "2", "3")
        g.add_edge("e3", "1", "3")
        return g

    def test_outgoing_edges(self) -> None:
        """Get outgoing edges from a node."""
        g = self._build_triangle()
        outgoing = g.get_outgoing_edges("1")
        assert len(outgoing) == TWO_EDGES

    def test_incoming_edges(self) -> None:
        """Get incoming edges to a node."""
        g = self._build_triangle()
        incoming = g.get_incoming_edges("3")
        assert len(incoming) == TWO_EDGES

    def test_neighbors_outgoing(self) -> None:
        """Get outgoing neighbors of a node."""
        g = self._build_triangle()
        neighbors = g.get_neighbors("1", direction="outgoing")
        assert len(neighbors) == TWO_NODES

    def test_neighbors_incoming(self) -> None:
        """Get incoming neighbors of a node."""
        g = self._build_triangle()
        neighbors = g.get_neighbors("3", direction="incoming")
        assert len(neighbors) == TWO_NODES

    def test_neighbors_both(self) -> None:
        """Get all neighbors (both directions)."""
        g = self._build_triangle()
        neighbors = g.get_neighbors("2", direction="both")
        assert len(neighbors) == TWO_NODES

    def test_out_degree(self) -> None:
        """Count outgoing edges."""
        g = self._build_triangle()
        assert g.out_degree("1") == TWO_EDGES

    def test_in_degree(self) -> None:
        """Count incoming edges."""
        g = self._build_triangle()
        assert g.in_degree("3") == TWO_EDGES

    def test_degree(self) -> None:
        """Count total edges (in + out)."""
        g = self._build_triangle()
        assert g.degree("2") == TWO_EDGES

    def test_neighbors_missing_node_raises(self) -> None:
        """Get neighbors of a missing node raises NodeNotFoundError."""
        g = Graph()
        with pytest.raises(NodeNotFoundError):
            g.get_neighbors("missing")


class TestGraphSerialization:
    """Test graph serialization to/from dictionaries."""

    def test_to_dict(self) -> None:
        """Serialize a graph to a dictionary."""
        g = Graph()
        g.add_node("1", label="Person")
        g.add_node("2", label="City")
        g.add_edge("e1", "1", "2", rel_type="LIVES_IN")
        data = g.to_dict()
        assert isinstance(data["nodes"], list)
        assert isinstance(data["edges"], list)

    def test_from_dict(self) -> None:
        """Deserialize a graph from a dictionary."""
        data: dict[str, object] = {
            "nodes": [
                {"node_id": "1", "label": "Person", "properties": {}},
                {"node_id": "2", "label": "City", "properties": {}},
            ],
            "edges": [
                {
                    "edge_id": "e1",
                    "source_id": "1",
                    "target_id": "2",
                    "rel_type": "LIVES_IN",
                    "properties": {},
                },
            ],
        }
        g = Graph.from_dict(data)
        assert g.node_count == TWO_NODES
        assert g.edge_count == ONE_EDGE

    def test_round_trip(self) -> None:
        """Serialize then deserialize preserves structure."""
        g = Graph()
        g.add_node("1", label="A")
        g.add_node("2", label="B")
        g.add_edge("e1", "1", "2", rel_type="REL")
        restored = Graph.from_dict(g.to_dict())
        assert restored.node_count == g.node_count
        assert restored.edge_count == g.edge_count

    def test_from_dict_edge_to_missing_node_raises(self) -> None:
        """An edge referencing a node that was not loaded raises NodeNotFoundError."""
        data: dict[str, object] = {
            "nodes": [
                {"node_id": "1", "label": "Person", "properties": {}},
            ],
            "edges": [
                {
                    "edge_id": "e1",
                    "source_id": "1",
                    "target_id": "ghost",
                    "rel_type": "KNOWS",
                    "properties": {},
                },
            ],
        }
        with pytest.raises(NodeNotFoundError):
            Graph.from_dict(data)
