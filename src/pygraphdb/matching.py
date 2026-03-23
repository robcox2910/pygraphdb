"""Pattern matching -- find nodes and edges that match criteria.

Imagine you're at a huge party and you want to find everyone who:
- Is a "Student" (label matching)
- Likes pizza (property matching)
- Is over 12 years old (property comparison)

Pattern matching lets you search through your graph and find exactly
the nodes or edges you're looking for, like a filter on Instagram
but for graph data!

Example:
    >>> from pygraphdb.graph import Graph
    >>> from pygraphdb.matching import find_nodes
    >>> g = Graph()
    >>> g.add_node("1", label="Person", properties={"name": "Alice", "age": 13})
    >>> g.add_node("2", label="Person", properties={"name": "Bob", "age": 14})
    >>> g.add_node("3", label="City", properties={"name": "London"})
    >>> people = find_nodes(g, label="Person")
    >>> len(people)
    2

"""

from pygraphdb.edge import Edge
from pygraphdb.graph import Graph
from pygraphdb.node import Node


def find_nodes(
    graph: Graph,
    *,
    label: str | None = None,
    properties: dict[str, object] | None = None,
) -> list[Node]:
    """Find all nodes matching the given label and/or properties.

    Like filtering your contact list: show me everyone who is a
    "Student" and has "age" equal to 13.

    Args:
        graph: The graph to search.
        label: If provided, only match nodes with this label.
        properties: If provided, only match nodes that have all these
            key-value pairs in their properties.

    Returns:
        A list of matching nodes.

    """
    results: list[Node] = []
    for node in graph.get_all_nodes():
        if label is not None and node.label != label:
            continue
        if properties is not None and not _properties_match(node.properties, properties):
            continue
        results.append(node)
    return results


def find_edges(
    graph: Graph,
    *,
    rel_type: str | None = None,
    properties: dict[str, object] | None = None,
    source_id: str | None = None,
    target_id: str | None = None,
) -> list[Edge]:
    """Find all edges matching the given criteria.

    Like searching for specific kinds of relationships: show me all
    "FRIENDS_WITH" connections, or all edges going from Alice to anyone.

    Args:
        graph: The graph to search.
        rel_type: If provided, only match edges with this relationship type.
        properties: If provided, only match edges that have all these
            key-value pairs in their properties.
        source_id: If provided, only match edges from this source node.
        target_id: If provided, only match edges to this target node.

    Returns:
        A list of matching edges.

    """
    results: list[Edge] = []
    for edge in graph.get_all_edges():
        if rel_type is not None and edge.rel_type != rel_type:
            continue
        if properties is not None and not _properties_match(edge.properties, properties):
            continue
        if source_id is not None and edge.source_id != source_id:
            continue
        if target_id is not None and edge.target_id != target_id:
            continue
        results.append(edge)
    return results


def _properties_match(actual: dict[str, object], expected: dict[str, object]) -> bool:
    """Check whether all expected properties exist in the actual properties.

    Args:
        actual: The actual properties dictionary.
        expected: The expected key-value pairs.

    Returns:
        True if all expected pairs are found in actual.

    """
    return all(actual.get(k) == v for k, v in expected.items())
