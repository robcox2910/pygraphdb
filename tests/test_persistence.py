"""Test saving and loading graphs to/from JSON."""

from pathlib import Path

from pygraphdb.graph import Graph
from pygraphdb.persistence import graph_from_json, graph_to_json, load_graph, save_graph

TWO_NODES = 2
ONE_EDGE = 1


def _build_simple_graph() -> Graph:
    """Build a simple graph for persistence tests."""
    g = Graph()
    g.add_node("1", label="Person", properties={"name": "Alice"})
    g.add_node("2", label="Person", properties={"name": "Bob"})
    g.add_edge("e1", "1", "2", rel_type="KNOWS")
    return g


class TestFilePersistence:
    """Test saving/loading to JSON files."""

    def test_save_and_load(self, tmp_path: Path) -> None:
        """Save a graph to disk and load it back."""
        g = _build_simple_graph()
        file_path = tmp_path / "test_graph.json"
        save_graph(g, file_path)
        loaded = load_graph(file_path)
        assert loaded.node_count == TWO_NODES
        assert loaded.edge_count == ONE_EDGE
        assert loaded.get_node("1").label == "Person"

    def test_save_creates_file(self, tmp_path: Path) -> None:
        """Save creates a JSON file on disk."""
        g = _build_simple_graph()
        file_path = tmp_path / "output.json"
        save_graph(g, file_path)
        assert file_path.exists()

    def test_save_string_path(self, tmp_path: Path) -> None:
        """Save works with a string path (not just Path object)."""
        g = _build_simple_graph()
        file_path = str(tmp_path / "string_path.json")
        save_graph(g, file_path)
        loaded = load_graph(file_path)
        assert loaded.node_count == TWO_NODES

    def test_round_trip_preserves_properties(self, tmp_path: Path) -> None:
        """Save and load preserves node and edge properties."""
        g = _build_simple_graph()
        file_path = tmp_path / "props.json"
        save_graph(g, file_path)
        loaded = load_graph(file_path)
        alice = loaded.get_node("1")
        assert alice.properties["name"] == "Alice"
        edge = loaded.get_edge("e1")
        assert edge.rel_type == "KNOWS"


class TestJsonSerialization:
    """Test in-memory JSON serialization."""

    def test_to_json_string(self) -> None:
        """Convert a graph to a JSON string."""
        g = _build_simple_graph()
        json_str = graph_to_json(g)
        assert '"nodes"' in json_str
        assert '"edges"' in json_str

    def test_from_json_string(self) -> None:
        """Restore a graph from a JSON string."""
        g = _build_simple_graph()
        json_str = graph_to_json(g)
        restored = graph_from_json(json_str)
        assert restored.node_count == TWO_NODES
        assert restored.edge_count == ONE_EDGE

    def test_round_trip_json(self) -> None:
        """JSON round-trip preserves all data."""
        g = _build_simple_graph()
        restored = graph_from_json(graph_to_json(g))
        assert restored.get_node("1").properties["name"] == "Alice"
        assert restored.get_edge("e1").rel_type == "KNOWS"
