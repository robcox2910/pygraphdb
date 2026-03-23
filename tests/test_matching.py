"""Test pattern matching on nodes and edges."""

from pygraphdb.graph import Graph
from pygraphdb.matching import find_edges, find_nodes

TWO_RESULTS = 2
ONE_RESULT = 1
ZERO_RESULTS = 0


def _build_social_graph() -> Graph:
    """Build a small social graph for testing."""
    g = Graph()
    g.add_node("1", label="Person", properties={"name": "Alice", "age": 13})
    g.add_node("2", label="Person", properties={"name": "Bob", "age": 14})
    g.add_node("3", label="City", properties={"name": "London"})
    g.add_edge("e1", "1", "2", rel_type="KNOWS", properties={"since": 2023})
    g.add_edge("e2", "1", "3", rel_type="LIVES_IN")
    g.add_edge("e3", "2", "3", rel_type="LIVES_IN")
    return g


class TestFindNodes:
    """Test finding nodes by label and properties."""

    def test_find_by_label(self) -> None:
        """Find nodes by label."""
        g = _build_social_graph()
        people = find_nodes(g, label="Person")
        assert len(people) == TWO_RESULTS

    def test_find_by_properties(self) -> None:
        """Find nodes by property match."""
        g = _build_social_graph()
        results = find_nodes(g, properties={"name": "Alice"})
        assert len(results) == ONE_RESULT
        assert results[0].node_id == "1"

    def test_find_by_label_and_properties(self) -> None:
        """Find nodes by both label and properties."""
        g = _build_social_graph()
        expected_age = 14
        results = find_nodes(g, label="Person", properties={"age": expected_age})
        assert len(results) == ONE_RESULT
        assert results[0].properties["name"] == "Bob"

    def test_find_no_match(self) -> None:
        """Find returns empty when nothing matches."""
        g = _build_social_graph()
        results = find_nodes(g, label="Animal")
        assert len(results) == ZERO_RESULTS

    def test_find_all_when_no_criteria(self) -> None:
        """Find with no criteria returns all nodes."""
        g = _build_social_graph()
        results = find_nodes(g)
        node_count = 3
        assert len(results) == node_count


class TestFindEdges:
    """Test finding edges by type, properties, and endpoints."""

    def test_find_by_rel_type(self) -> None:
        """Find edges by relationship type."""
        g = _build_social_graph()
        results = find_edges(g, rel_type="LIVES_IN")
        assert len(results) == TWO_RESULTS

    def test_find_by_source(self) -> None:
        """Find edges by source node ID."""
        g = _build_social_graph()
        results = find_edges(g, source_id="1")
        assert len(results) == TWO_RESULTS

    def test_find_by_target(self) -> None:
        """Find edges by target node ID."""
        g = _build_social_graph()
        results = find_edges(g, target_id="3")
        assert len(results) == TWO_RESULTS

    def test_find_by_properties(self) -> None:
        """Find edges by property match."""
        g = _build_social_graph()
        expected_year = 2023
        results = find_edges(g, properties={"since": expected_year})
        assert len(results) == ONE_RESULT

    def test_find_by_type_and_source(self) -> None:
        """Find edges by both type and source."""
        g = _build_social_graph()
        results = find_edges(g, rel_type="LIVES_IN", source_id="1")
        assert len(results) == ONE_RESULT

    def test_find_no_match(self) -> None:
        """Find returns empty when nothing matches."""
        g = _build_social_graph()
        results = find_edges(g, rel_type="HATES")
        assert len(results) == ZERO_RESULTS
