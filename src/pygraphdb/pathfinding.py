"""Shortest path finding -- like GPS directions for your graph.

When you ask Google Maps for directions, it finds the route with the
fewest turns (or shortest distance). Our pathfinding does the same
thing for graphs -- it finds the path with the fewest edges between
two nodes.

We use BFS (breadth-first search) because it naturally finds the
shortest path in an unweighted graph. It explores nodes layer by
layer, so the first time it reaches the destination, that path is
guaranteed to be the shortest!

Example:
    >>> from pygraphdb.graph import Graph
    >>> from pygraphdb.pathfinding import shortest_path
    >>> g = Graph()
    >>> for nid in ["a", "b", "c", "d"]:
    ...     g.add_node(nid)
    >>> g.add_edge("e1", "a", "b")
    >>> g.add_edge("e2", "b", "c")
    >>> g.add_edge("e3", "a", "d")
    >>> g.add_edge("e4", "d", "c")
    >>> path = shortest_path(g, "a", "c")
    >>> [n.node_id for n in path]
    ['a', 'b', 'c']

"""

from collections import deque

from pygraphdb.graph import Graph
from pygraphdb.node import Node


def shortest_path(graph: Graph, start_id: str, end_id: str) -> list[Node]:
    """Find the shortest path between two nodes using BFS.

    Like asking for GPS directions: find the route with the fewest
    stops between your starting point and your destination.

    Args:
        graph: The graph to search.
        start_id: The ID of the starting node.
        end_id: The ID of the destination node.

    Returns:
        A list of nodes forming the shortest path (including start and end).
        An empty list if no path exists.

    Raises:
        NodeNotFoundError: If start or end node does not exist.

    """
    graph.get_node(start_id)  # Validate existence
    graph.get_node(end_id)  # Validate existence

    if start_id == end_id:
        return [graph.get_node(start_id)]

    visited: set[str] = {start_id}
    # Each queue entry is (current_node_id, path_so_far)
    queue: deque[tuple[str, list[str]]] = deque([(start_id, [start_id])])

    while queue:
        current_id, path = queue.popleft()
        for edge in graph.get_outgoing_edges(current_id):
            neighbor_id = edge.target_id
            if neighbor_id == end_id:
                full_path = [*path, neighbor_id]
                return [graph.get_node(nid) for nid in full_path]
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                queue.append((neighbor_id, [*path, neighbor_id]))

    return []


def all_paths(
    graph: Graph,
    start_id: str,
    end_id: str,
    *,
    max_depth: int = 10,
) -> list[list[Node]]:
    """Find all paths between two nodes up to a maximum depth.

    Like finding every possible route between your house and school,
    not just the shortest one.

    Args:
        graph: The graph to search.
        start_id: The ID of the starting node.
        end_id: The ID of the destination node.
        max_depth: Maximum path length to consider.

    Returns:
        A list of paths, where each path is a list of nodes.

    Raises:
        NodeNotFoundError: If start or end node does not exist.

    """
    graph.get_node(start_id)  # Validate existence
    graph.get_node(end_id)  # Validate existence

    results: list[list[str]] = []
    _all_paths_helper(graph, start_id, end_id, [start_id], set(), results, max_depth)
    return [[graph.get_node(nid) for nid in path] for path in results]


def _all_paths_helper(
    graph: Graph,
    current_id: str,
    end_id: str,
    current_path: list[str],
    visited: set[str],
    results: list[list[str]],
    max_depth: int,
) -> None:
    """Recursive helper for finding all paths.

    Args:
        graph: The graph to search.
        current_id: Current position in the traversal.
        end_id: The destination node ID.
        current_path: Path taken so far.
        visited: Set of visited node IDs.
        results: Accumulator for found paths.
        max_depth: Maximum remaining depth.

    """
    if current_id == end_id:
        results.append(list(current_path))
        return

    if max_depth <= 0:
        return

    visited.add(current_id)
    for edge in graph.get_outgoing_edges(current_id):
        if edge.target_id not in visited:
            current_path.append(edge.target_id)
            _all_paths_helper(
                graph, edge.target_id, end_id, current_path, visited, results, max_depth - 1
            )
            current_path.pop()
    visited.discard(current_id)
