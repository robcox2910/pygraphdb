"""Test saving and loading graphs to/from JSON."""

import os
from pathlib import Path

import pytest

from pygraphdb.errors import GraphError, PersistenceError
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


class _SimulatedCrashError(OSError):
    """Stands in for the power going out part-way through a save."""


def test_interrupted_save_keeps_the_previous_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regression: a crash mid-save used to leave a truncated, unloadable file."""
    graph = Graph()
    graph.add_node("a")
    path = tmp_path / "data.json"
    save_graph(graph, path)
    before = path.read_bytes()
    graph.add_node("b")

    def write_half_then_crash(self: Path, data: str, *_args: object, **_kwargs: object) -> int:
        with self.open("w", encoding="utf-8") as handle:
            handle.write(data[: len(data) // 2])
        raise _SimulatedCrashError

    def crash(*_args: object) -> None:
        raise _SimulatedCrashError

    monkeypatch.setattr(Path, "write_text", write_half_then_crash)
    monkeypatch.setattr(os, "replace", crash)
    with pytest.raises(_SimulatedCrashError):
        save_graph(graph, path)
    monkeypatch.undo()
    assert path.read_bytes() == before
    load_graph(path)
    assert [p.name for p in tmp_path.iterdir()] == ["data.json"]


class TestUnreadableSaveFiles:
    """A missing or damaged save file raises PersistenceError, naming the file."""

    def test_missing_file_raises_persistence_error(self, tmp_path: Path) -> None:
        """Loading a file that isn't there is a PersistenceError."""
        with pytest.raises(PersistenceError, match=r"missing\.json"):
            load_graph(tmp_path / "missing.json")

    def test_bad_json_raises_persistence_error_naming_the_file(self, tmp_path: Path) -> None:
        """A scribbled-on file is a PersistenceError that names the file."""
        path = tmp_path / "saved.json"
        path.write_text("{not json", encoding="utf-8")
        with pytest.raises(PersistenceError, match=r"saved\.json"):
            load_graph(path)

    def test_wrong_shape_raises_persistence_error(self, tmp_path: Path) -> None:
        """Valid JSON that isn't a saved graph is a PersistenceError."""
        path = tmp_path / "saved.json"
        path.write_text('{"something": "else"}', encoding="utf-8")
        with pytest.raises(PersistenceError, match=r"saved\.json"):
            load_graph(path)

    def test_persistence_error_is_part_of_the_library_errors(self) -> None:
        """PersistenceError belongs to the library's own family of errors."""
        assert issubclass(PersistenceError, GraphError)
