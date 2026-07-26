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

    conditions = _parse_conditions(where_clause, {var_name})

    results: list[Node] = []
    for node in graph.get_all_nodes():
        if node.label != label:
            continue
        if not _node_matches(node, var_name, conditions):
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

    # WHERE conditions may reference either the source or the target variable.
    conditions = _parse_conditions(where_clause, {source_var, target_var})

    results: list[Node] = []
    seen_ids: set[str] = set()

    for node in graph.get_all_nodes():
        if node.label != source_label:
            continue
        if not _node_matches(node, source_var, conditions):
            continue

        for edge in graph.get_outgoing_edges(node.node_id):
            if edge.rel_type != rel_type:
                continue
            target = graph.get_node(edge.target_id)
            if not _node_matches(target, target_var, conditions):
                continue

            if return_var == source_var:
                # One matching edge is enough to keep the source node.
                if node.node_id not in seen_ids:
                    seen_ids.add(node.node_id)
                    results.append(node)
                break
            if target.node_id not in seen_ids:
                seen_ids.add(target.node_id)
                results.append(target)

    return results


def _parse_conditions(
    where_clause: str | None,
    valid_vars: set[str],
) -> list[tuple[str, str, str]]:
    """Turn a raw WHERE clause into a list of (var, prop, value) conditions.

    Args:
        where_clause: The raw WHERE clause string, or None if there was no WHERE.
        valid_vars: The variable names the query actually defines.

    Returns:
        A list of parsed conditions (empty if there was no WHERE clause).

    Raises:
        QuerySyntaxError: If a WHERE clause is present but nothing parses
            (for example an unquoted value), or a condition refers to a
            variable the query never defined.

    """
    if where_clause is None:
        return []
    conditions: list[tuple[str, str, str]] = _WHERE_CONDITION.findall(where_clause)
    if not conditions:
        msg = (
            f"Cannot understand WHERE clause: {where_clause!r} "
            '(values must be quoted, e.g. n.name = "Alice")'
        )
        raise QuerySyntaxError(msg)
    for cond_var, _prop_name, _prop_value in conditions:
        if cond_var not in valid_vars:
            msg = f"WHERE refers to unknown variable '{cond_var}'"
            raise QuerySyntaxError(msg)
    return conditions


def _node_matches(node: Node, var_name: str, conditions: list[tuple[str, str, str]]) -> bool:
    """Check whether a node satisfies the conditions aimed at its variable.

    Only conditions whose variable equals ``var_name`` apply here; conditions
    for other variables are checked against their own nodes elsewhere.

    Args:
        node: The node to test.
        var_name: The variable this node is bound to.
        conditions: All parsed WHERE conditions.

    Returns:
        True if the node satisfies every condition aimed at ``var_name``.

    """
    for cond_var, prop_name, prop_value in conditions:
        if cond_var != var_name:
            continue
        if str(node.get_property(prop_name)) != prop_value:
            return False
    return True
