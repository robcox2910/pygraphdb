"""Graph traversal algorithms -- BFS and DFS.

Imagine you're exploring a maze. There are two main strategies:

**BFS (Breadth-First Search)** -- Like ripples in a pond. You explore
all rooms one step away first, then all rooms two steps away, and so on.
This guarantees you find the shortest path (fewest steps) first.

**DFS (Depth-First Search)** -- Like following one tunnel as deep as
you can go before backtracking. You pick a direction and keep going
until you hit a dead end, then you go back and try another path.

Both algorithms visit every reachable node exactly once, but in
different orders. BFS uses a queue (first-in, first-out), while
DFS uses a stack (last-in, first-out).

Example:
    >>> from pygraphdb.graph import Graph
    >>> from pygraphdb.traversal import bfs, dfs
    >>> g = Graph()
    >>> g.add_node("a")
    >>> g.add_node("b")
    >>> g.add_node("c")
    >>> g.add_edge("e1", "a", "b")
    >>> g.add_edge("e2", "b", "c")
    >>> [n.node_id for n in bfs(g, "a")]
    ['a', 'b', 'c']

"""

from collections import deque

from pygraphdb.graph import Graph
from pygraphdb.node import Node


def bfs(graph: Graph, start_id: str) -> list[Node]:
    """Perform a breadth-first search starting from a given node.

    Like ripples spreading outward from a stone dropped in water:
    visit all neighbors first, then neighbors-of-neighbors, etc.

    Args:
        graph: The graph to traverse.
        start_id: The ID of the starting node.

    Returns:
        A list of nodes in BFS visit order.

    Raises:
        NodeNotFoundError: If the start node does not exist.

    """
    graph.get_node(start_id)  # Validate existence
    visited: set[str] = set()
    result: list[Node] = []
    queue: deque[str] = deque([start_id])
    visited.add(start_id)

    while queue:
        current_id = queue.popleft()
        node = graph.get_node(current_id)
        result.append(node)
        for edge in graph.get_outgoing_edges(current_id):
            if edge.target_id not in visited:
                visited.add(edge.target_id)
                queue.append(edge.target_id)

    return result


def dfs(graph: Graph, start_id: str) -> list[Node]:
    """Perform a depth-first search starting from a given node.

    Like exploring a cave -- go as deep as you can down one tunnel,
    then backtrack and try the next tunnel.

    Args:
        graph: The graph to traverse.
        start_id: The ID of the starting node.

    Returns:
        A list of nodes in DFS visit order.

    Raises:
        NodeNotFoundError: If the start node does not exist.

    """
    graph.get_node(start_id)  # Validate existence
    visited: set[str] = set()
    result: list[Node] = []
    stack: list[str] = [start_id]

    while stack:
        current_id = stack.pop()
        if current_id in visited:
            continue
        visited.add(current_id)
        node = graph.get_node(current_id)
        result.append(node)
        # Add neighbors in reverse order so we visit them in a predictable order
        outgoing = graph.get_outgoing_edges(current_id)
        stack.extend(edge.target_id for edge in reversed(outgoing) if edge.target_id not in visited)

    return result
