"""Simple Cypher-like query language parser and executor.

Real graph databases like Neo4j use a language called Cypher to ask
questions about the graph. It's like SQL but for graphs! Our version
is simplified but follows the same idea.

Think of it like asking questions in a specific format:
- "MATCH" means "find me..."
- "(n:Person)" means "a node labeled Person, call it n"
- "-[:KNOWS]->" means "connected by a KNOWS relationship"
- "WHERE n.name = 'Alice'" means "but only if the name is Alice"
- "RETURN m" means "give me back the thing called m"

Supported query format:
    MATCH (n:Label)-[:REL_TYPE]->(m) WHERE n.prop = "value" RETURN m
    MATCH (n:Label) RETURN n
    MATCH (n:Label) WHERE n.prop = "value" RETURN n

Example:
    >>> from pygraphdb.graph import Graph
    >>> from pygraphdb.query import execute_query
    >>> g = Graph()
    >>> g.add_node("1", label="Person", properties={"name": "Alice"})
    >>> g.add_node("2", label="Person", properties={"name": "Bob"})
    >>> g.add_edge("e1", "1", "2", rel_type="KNOWS")
    >>> results = execute_query(g, 'MATCH (n:Person) WHERE n.name = "Alice" RETURN n')
    >>> len(results)
    1

"""

import re

from pygraphdb.errors import QuerySyntaxError
from pygraphdb.graph import Graph
from pygraphdb.node import Node

# Pattern for: MATCH (var:Label)-[:REL]->(var2) WHERE var.prop = "val" RETURN var2
_PATTERN_WITH_EDGE = re.compile(
    r"MATCH\s+\((\w+):(\w+)\)"  # (n:Label)
    r"\s*-\[:(\w+)\]->\s*"  # -[:REL]->
    r"\((\w+)\)"  # (m)
    r"(?:\s+WHERE\s+(.+?))?"  # optional WHERE clause
    r"\s+RETURN\s+(\w+)",  # RETURN var
    re.IGNORECASE,
)

# Pattern for: MATCH (var:Label) WHERE var.prop = "val" RETURN var
_PATTERN_NODE_ONLY = re.compile(
    r"MATCH\s+\((\w+):(\w+)\)"  # (n:Label)
    r"(?:\s+WHERE\s+(.+?))?"  # optional WHERE clause
    r"\s+RETURN\s+(\w+)",  # RETURN var
    re.IGNORECASE,
)

# Pattern for WHERE conditions: var.prop = "value" or var.prop = 'value'
_WHERE_CONDITION = re.compile(
    r"(\w+)\.(\w+)\s*=\s*[\"']([^\"']*)[\"']",
)


def execute_query(graph: Graph, query: str) -> list[Node]:
    """Execute a simple Cypher-like query against the graph.

    Parse and run a query string to find matching nodes.

    Supported patterns:
        - ``MATCH (n:Label) RETURN n``
        - ``MATCH (n:Label) WHERE n.prop = "value" RETURN n``
        - ``MATCH (n:Label)-[:REL]->(m) RETURN m``
        - ``MATCH (n:Label)-[:REL]->(m) WHERE n.prop = "value" RETURN m``

    Args:
        graph: The graph to query.
        query: A Cypher-like query string.

    Returns:
        A list of nodes matching the query.

    Raises:
        QuerySyntaxError: If the query cannot be parsed.

    """
    query = query.strip()

    # Try edge pattern first (more specific)
    match = _PATTERN_WITH_EDGE.match(query)
    if match:
        return _execute_edge_query(graph, match)

    # Try node-only pattern
    match = _PATTERN_NODE_ONLY.match(query)
    if match:
        return _execute_node_query(graph, match)

    msg = f"Cannot parse query: {query}"
    raise QuerySyntaxError(msg)


def _execute_node_query(graph: Graph, match: re.Match[str]) -> list[Node]:
    """Execute a node-only query (no edge pattern).

    Args:
        graph: The graph to query.
        match: The regex match object.

    Returns:
        A list of matching nodes.

    """
    var_name = match.group(1)
    label = match.group(2)
    where_clause = match.group(3)
    return_var = match.group(4)

    if return_var != var_name:
        msg = f"RETURN variable '{return_var}' not defined in MATCH"
        raise QuerySyntaxError(msg)

    results: list[Node] = []
    for node in graph.get_all_nodes():
        if node.label != label:
            continue
        if where_clause and not _evaluate_where(node, var_name, where_clause):
            continue
        results.append(node)
    return results


def _execute_edge_query(graph: Graph, match: re.Match[str]) -> list[Node]:
    """Execute a query with an edge pattern.

    Args:
        graph: The graph to query.
        match: The regex match object.

    Returns:
        A list of matching nodes.

    """
    source_var = match.group(1)
    source_label = match.group(2)
    rel_type = match.group(3)
    target_var = match.group(4)
    where_clause = match.group(5)
    return_var = match.group(6)

    if return_var not in (source_var, target_var):
        msg = f"RETURN variable '{return_var}' not defined in MATCH"
        raise QuerySyntaxError(msg)

    results: list[Node] = []
    seen_ids: set[str] = set()

    for node in graph.get_all_nodes():
        if node.label != source_label:
            continue
        if where_clause and not _evaluate_where(node, source_var, where_clause):
            continue

        if return_var == source_var:
            # Check that at least one matching edge exists
            outgoing = graph.get_outgoing_edges(node.node_id)
            has_matching_edge = any(e.rel_type == rel_type for e in outgoing)
            if has_matching_edge and node.node_id not in seen_ids:
                seen_ids.add(node.node_id)
                results.append(node)
        else:
            # Return target nodes
            for edge in graph.get_outgoing_edges(node.node_id):
                if edge.rel_type == rel_type and edge.target_id not in seen_ids:
                    seen_ids.add(edge.target_id)
                    results.append(graph.get_node(edge.target_id))

    return results


def _evaluate_where(node: Node, var_name: str, where_clause: str) -> bool:
    """Evaluate a WHERE clause against a node.

    Args:
        node: The node to test.
        var_name: The variable name used in the query.
        where_clause: The raw WHERE clause string.

    Returns:
        True if the node satisfies all conditions.

    """
    conditions = _WHERE_CONDITION.findall(where_clause)
    for cond_var, prop_name, prop_value in conditions:
        if cond_var != var_name:
            continue
        actual = node.get_property(prop_name)
        if str(actual) != prop_value:
            return False
    return True
