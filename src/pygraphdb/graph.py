"""Graph -- the container that holds nodes and edges together.

Imagine a giant whiteboard in your classroom. You can stick Post-it notes
on it (those are nodes) and draw lines between them (those are edges).
The whiteboard itself is the Graph -- it keeps track of everything and
lets you add, find, update, or remove nodes and edges.

This is the heart of PyGraphDB. Everything else (traversal, queries,
persistence) builds on top of this container.

Example:
    >>> from pygraphdb.graph import Graph
    >>> g = Graph()
    >>> g.add_node("alice", label="Person", properties={"name": "Alice"})
    >>> g.add_node("bob", label="Person", properties={"name": "Bob"})
    >>> g.add_edge("e1", "alice", "bob", rel_type="KNOWS")
    >>> g.get_node("alice").properties["name"]
    'Alice'

"""

from pygraphdb.edge import Edge
from pygraphdb.errors import (
    DuplicateEdgeError,
    DuplicateNodeError,
    EdgeNotFoundError,
    NodeNotFoundError,
)
from pygraphdb.node import Node


class Graph:
    """A container for nodes and edges forming a directed graph.

    Think of the Graph as a city map:
    - Nodes are buildings (houses, schools, shops)
    - Edges are roads connecting them
    - The Graph keeps a directory of all buildings and all roads

    You can add, look up, update, and remove both nodes and edges.
    """

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self._nodes: dict[str, Node] = {}
        self._edges: dict[str, Edge] = {}

    @property
    def node_count(self) -> int:
        """Return the number of nodes in the graph."""
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        """Return the number of edges in the graph."""
        return len(self._edges)

    # --- Node CRUD ---

    def add_node(
        self,
        node_id: str,
        *,
        label: str = "",
        properties: dict[str, object] | None = None,
    ) -> Node:
        """Add a new node to the graph.

        Args:
            node_id: A unique identifier for the node.
            label: An optional category label.
            properties: Optional key-value attributes.

        Returns:
            The newly created Node.

        Raises:
            DuplicateNodeError: If a node with this ID already exists.

        """
        if node_id in self._nodes:
            msg = f"Node '{node_id}' already exists"
            raise DuplicateNodeError(msg)
        node = Node(node_id=node_id, label=label, properties=properties or {})
        self._nodes[node_id] = node
        return node

    def get_node(self, node_id: str) -> Node:
        """Retrieve a node by its ID.

        Args:
            node_id: The unique identifier of the node.

        Returns:
            The matching Node.

        Raises:
            NodeNotFoundError: If no node with this ID exists.

        """
        if node_id not in self._nodes:
            msg = f"Node '{node_id}' not found"
            raise NodeNotFoundError(msg)
        return self._nodes[node_id]

    def has_node(self, node_id: str) -> bool:
        """Check whether a node with the given ID exists.

        Args:
            node_id: The node ID to check.

        Returns:
            True if the node exists, False otherwise.

        """
        return node_id in self._nodes

    def update_node(
        self,
        node_id: str,
        *,
        label: str | None = None,
        properties: dict[str, object] | None = None,
    ) -> Node:
        """Update an existing node's label and/or properties.

        Args:
            node_id: The ID of the node to update.
            label: New label (if provided).
            properties: Properties to merge in (if provided).

        Returns:
            The updated Node.

        Raises:
            NodeNotFoundError: If the node does not exist.

        """
        node = self.get_node(node_id)
        if label is not None:
            node.label = label
        if properties is not None:
            node.properties.update(properties)
        return node

    def remove_node(self, node_id: str) -> Node:
        """Remove a node and all its connected edges from the graph.

        Args:
            node_id: The ID of the node to remove.

        Returns:
            The removed Node.

        Raises:
            NodeNotFoundError: If the node does not exist.

        """
        node = self.get_node(node_id)
        # Remove all edges connected to this node
        edges_to_remove = [
            eid for eid, edge in self._edges.items() if node_id in (edge.source_id, edge.target_id)
        ]
        for eid in edges_to_remove:
            del self._edges[eid]
        del self._nodes[node_id]
        return node

    def get_all_nodes(self) -> list[Node]:
        """Return a list of all nodes in the graph.

        Returns:
            A list of all Node objects.

        """
        return list(self._nodes.values())

    # --- Edge CRUD ---

    def add_edge(
        self,
        edge_id: str,
        source_id: str,
        target_id: str,
        *,
        rel_type: str = "",
        properties: dict[str, object] | None = None,
    ) -> Edge:
        """Add a new directed edge between two nodes.

        Args:
            edge_id: A unique identifier for the edge.
            source_id: The ID of the source node.
            target_id: The ID of the target node.
            rel_type: The relationship type.
            properties: Optional key-value attributes.

        Returns:
            The newly created Edge.

        Raises:
            DuplicateEdgeError: If an edge with this ID already exists.
            NodeNotFoundError: If source or target node does not exist.

        """
        if edge_id in self._edges:
            msg = f"Edge '{edge_id}' already exists"
            raise DuplicateEdgeError(msg)
        if source_id not in self._nodes:
            msg = f"Source node '{source_id}' not found"
            raise NodeNotFoundError(msg)
        if target_id not in self._nodes:
            msg = f"Target node '{target_id}' not found"
            raise NodeNotFoundError(msg)
        edge = Edge(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            rel_type=rel_type,
            properties=properties or {},
        )
        self._edges[edge_id] = edge
        return edge

    def get_edge(self, edge_id: str) -> Edge:
        """Retrieve an edge by its ID.

        Args:
            edge_id: The unique identifier of the edge.

        Returns:
            The matching Edge.

        Raises:
            EdgeNotFoundError: If no edge with this ID exists.

        """
        if edge_id not in self._edges:
            msg = f"Edge '{edge_id}' not found"
            raise EdgeNotFoundError(msg)
        return self._edges[edge_id]

    def has_edge(self, edge_id: str) -> bool:
        """Check whether an edge with the given ID exists.

        Args:
            edge_id: The edge ID to check.

        Returns:
            True if the edge exists, False otherwise.

        """
        return edge_id in self._edges

    def update_edge(
        self,
        edge_id: str,
        *,
        rel_type: str | None = None,
        properties: dict[str, object] | None = None,
    ) -> Edge:
        """Update an existing edge's type and/or properties.

        Args:
            edge_id: The ID of the edge to update.
            rel_type: New relationship type (if provided).
            properties: Properties to merge in (if provided).

        Returns:
            The updated Edge.

        Raises:
            EdgeNotFoundError: If the edge does not exist.

        """
        edge = self.get_edge(edge_id)
        if rel_type is not None:
            edge.rel_type = rel_type
        if properties is not None:
            edge.properties.update(properties)
        return edge

    def remove_edge(self, edge_id: str) -> Edge:
        """Remove an edge from the graph.

        Args:
            edge_id: The ID of the edge to remove.

        Returns:
            The removed Edge.

        Raises:
            EdgeNotFoundError: If the edge does not exist.

        """
        edge = self.get_edge(edge_id)
        del self._edges[edge_id]
        return edge

    def get_all_edges(self) -> list[Edge]:
        """Return a list of all edges in the graph.

        Returns:
            A list of all Edge objects.

        """
        return list(self._edges.values())

    # --- Neighbor / Degree queries ---

    def get_outgoing_edges(self, node_id: str) -> list[Edge]:
        """Get all edges going out from a node.

        Args:
            node_id: The source node ID.

        Returns:
            A list of outgoing edges.

        Raises:
            NodeNotFoundError: If the node does not exist.

        """
        self.get_node(node_id)  # Validate existence
        return [e for e in self._edges.values() if e.source_id == node_id]

    def get_incoming_edges(self, node_id: str) -> list[Edge]:
        """Get all edges coming into a node.

        Args:
            node_id: The target node ID.

        Returns:
            A list of incoming edges.

        Raises:
            NodeNotFoundError: If the node does not exist.

        """
        self.get_node(node_id)  # Validate existence
        return [e for e in self._edges.values() if e.target_id == node_id]

    def get_neighbors(
        self,
        node_id: str,
        *,
        direction: str = "both",
    ) -> list[Node]:
        """Get all nodes connected to a given node.

        Args:
            node_id: The node to find neighbors for.
            direction: One of "outgoing", "incoming", or "both".

        Returns:
            A list of neighboring nodes (no duplicates).

        Raises:
            NodeNotFoundError: If the node does not exist.

        """
        self.get_node(node_id)  # Validate existence
        neighbor_ids: set[str] = set()
        if direction in ("outgoing", "both"):
            for edge in self._edges.values():
                if edge.source_id == node_id:
                    neighbor_ids.add(edge.target_id)
        if direction in ("incoming", "both"):
            for edge in self._edges.values():
                if edge.target_id == node_id:
                    neighbor_ids.add(edge.source_id)
        return [self._nodes[nid] for nid in neighbor_ids]

    def out_degree(self, node_id: str) -> int:
        """Count outgoing edges from a node.

        Args:
            node_id: The node ID.

        Returns:
            The number of outgoing edges.

        """
        return len(self.get_outgoing_edges(node_id))

    def in_degree(self, node_id: str) -> int:
        """Count incoming edges to a node.

        Args:
            node_id: The node ID.

        Returns:
            The number of incoming edges.

        """
        return len(self.get_incoming_edges(node_id))

    def degree(self, node_id: str) -> int:
        """Count total edges connected to a node (in + out).

        Args:
            node_id: The node ID.

        Returns:
            The total degree.

        """
        return self.in_degree(node_id) + self.out_degree(node_id)

    def to_dict(self) -> dict[str, object]:
        """Serialize the entire graph to a dictionary.

        Returns:
            A dictionary with "nodes" and "edges" keys.

        """
        return {
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": [e.to_dict() for e in self._edges.values()],
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Graph:
        """Create a Graph from a dictionary.

        Args:
            data: A dictionary with "nodes" and "edges" lists.

        Returns:
            A new Graph instance.

        """
        graph = cls()
        raw_nodes = data.get("nodes")
        raw_edges = data.get("edges")
        if isinstance(raw_nodes, list):
            for item in raw_nodes:  # pyright: ignore[reportUnknownVariableType]
                if isinstance(item, dict):
                    node_data: dict[str, object] = {str(k): v for k, v in item.items()}  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
                    node = Node.from_dict(node_data)
                    graph._nodes[node.node_id] = node
        if isinstance(raw_edges, list):
            for item in raw_edges:  # pyright: ignore[reportUnknownVariableType]
                if isinstance(item, dict):
                    edge_data: dict[str, object] = {str(k): v for k, v in item.items()}  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
                    edge = Edge.from_dict(edge_data)
                    graph._edges[edge.edge_id] = edge
        return graph
