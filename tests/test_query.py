"""Test the Cypher-like query parser and executor."""

import pytest

from pygraphdb.errors import QuerySyntaxError
from pygraphdb.graph import Graph
from pygraphdb.query import execute_query

ONE_RESULT = 1
TWO_RESULTS = 2


def _build_query_graph() -> Graph:
    """Build a graph for query tests."""
    g = Graph()
    g.add_node("1", label="Person", properties={"name": "Alice", "age": "13"})
    g.add_node("2", label="Person", properties={"name": "Bob", "age": "14"})
    g.add_node("3", label="Person", properties={"name": "Charlie", "age": "13"})
    g.add_node("4", label="City", properties={"name": "London"})
    g.add_edge("e1", "1", "2", rel_type="KNOWS")
    g.add_edge("e2", "1", "3", rel_type="KNOWS")
    g.add_edge("e3", "2", "3", rel_type="KNOWS")
    g.add_edge("e4", "1", "4", rel_type="LIVES_IN")
    return g


class TestNodeQueries:
    """Test queries that match nodes only."""

    def test_match_by_label(self) -> None:
        """Match all nodes with a given label."""
        g = _build_query_graph()
        results = execute_query(g, "MATCH (n:Person) RETURN n")
        person_count = 3
        assert len(results) == person_count

    def test_match_by_label_and_where(self) -> None:
        """Match nodes with a label and WHERE condition."""
        g = _build_query_graph()
        results = execute_query(g, 'MATCH (n:Person) WHERE n.name = "Alice" RETURN n')
        assert len(results) == ONE_RESULT
        assert results[0].properties["name"] == "Alice"

    def test_match_city(self) -> None:
        """Match city nodes."""
        g = _build_query_graph()
        results = execute_query(g, "MATCH (c:City) RETURN c")
        assert len(results) == ONE_RESULT
        assert results[0].properties["name"] == "London"

    def test_match_no_results(self) -> None:
        """Match returns empty when nothing matches."""
        g = _build_query_graph()
        results = execute_query(g, "MATCH (n:Animal) RETURN n")
        assert len(results) == 0


class TestEdgeQueries:
    """Test queries that match edges (relationships)."""

    def test_match_with_edge_return_target(self) -> None:
        """Match nodes connected by an edge, return target."""
        g = _build_query_graph()
        results = execute_query(g, 'MATCH (n:Person)-[:KNOWS]->(m) WHERE n.name = "Alice" RETURN m')
        assert len(results) == TWO_RESULTS

    def test_match_with_edge_return_source(self) -> None:
        """Match and return the source node."""
        g = _build_query_graph()
        results = execute_query(g, 'MATCH (n:Person)-[:KNOWS]->(m) WHERE n.name = "Alice" RETURN n')
        assert len(results) == ONE_RESULT
        assert results[0].properties["name"] == "Alice"

    def test_match_lives_in(self) -> None:
        """Match LIVES_IN relationships."""
        g = _build_query_graph()
        results = execute_query(
            g, 'MATCH (n:Person)-[:LIVES_IN]->(m) WHERE n.name = "Alice" RETURN m'
        )
        assert len(results) == ONE_RESULT
        assert results[0].properties["name"] == "London"

    def test_match_edge_no_where(self) -> None:
        """Match edge pattern without a WHERE clause."""
        g = _build_query_graph()
        results = execute_query(g, "MATCH (n:Person)-[:KNOWS]->(m) RETURN m")
        # All KNOWS targets (Bob, Charlie from Alice; Charlie from Bob) -- deduplicated
        assert len(results) == TWO_RESULTS


class TestQueryErrors:
    """Test query error handling."""

    def test_invalid_syntax_raises(self) -> None:
        """Invalid query syntax raises QuerySyntaxError."""
        g = Graph()
        with pytest.raises(QuerySyntaxError):
            execute_query(g, "SELECT * FROM nodes")

    def test_undefined_return_var_raises(self) -> None:
        """RETURN a variable not defined in MATCH raises QuerySyntaxError."""
        g = Graph()
        with pytest.raises(QuerySyntaxError):
            execute_query(g, "MATCH (n:Person) RETURN x")
