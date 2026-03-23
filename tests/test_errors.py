"""Test custom exception hierarchy."""

from pygraphdb.errors import (
    DuplicateEdgeError,
    DuplicateNodeError,
    EdgeNotFoundError,
    GraphError,
    NodeNotFoundError,
    QuerySyntaxError,
)


class TestExceptionHierarchy:
    """Test that all custom exceptions inherit from GraphError."""

    def test_node_not_found_is_graph_error(self) -> None:
        """NodeNotFoundError inherits from GraphError."""
        assert issubclass(NodeNotFoundError, GraphError)

    def test_edge_not_found_is_graph_error(self) -> None:
        """EdgeNotFoundError inherits from GraphError."""
        assert issubclass(EdgeNotFoundError, GraphError)

    def test_duplicate_node_is_graph_error(self) -> None:
        """DuplicateNodeError inherits from GraphError."""
        assert issubclass(DuplicateNodeError, GraphError)

    def test_duplicate_edge_is_graph_error(self) -> None:
        """DuplicateEdgeError inherits from GraphError."""
        assert issubclass(DuplicateEdgeError, GraphError)

    def test_query_syntax_is_graph_error(self) -> None:
        """QuerySyntaxError inherits from GraphError."""
        assert issubclass(QuerySyntaxError, GraphError)

    def test_graph_error_is_exception(self) -> None:
        """GraphError inherits from Exception."""
        assert issubclass(GraphError, Exception)
