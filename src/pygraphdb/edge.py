"""Edge -- a relationship between two nodes in a graph database.

Picture two people at a party shaking hands. That handshake is an edge!
It connects one person (the source) to another (the target) and has a
type that describes the relationship ("FRIENDS_WITH", "KNOWS", "WORKS_AT").

Edges can also carry properties, just like friendships have qualities --
maybe you became friends in 2024, or you're "best friends" vs "acquaintances."

Edges in our graph are *directed* -- like a one-way street. "Alice FOLLOWS Bob"
doesn't automatically mean "Bob FOLLOWS Alice." If you want both directions,
you add two separate edges.

Example:
    >>> from pygraphdb.edge import Edge
    >>> friendship = Edge(
    ...     edge_id="e1",
    ...     source_id="alice",
    ...     target_id="bob",
    ...     rel_type="FRIENDS_WITH",
    ...     properties={"since": 2024},
    ... )
    >>> friendship.rel_type
    'FRIENDS_WITH'

"""

from dataclasses import dataclass, field


@dataclass
class Edge:
    """A directed relationship between two nodes.

    Think of an edge like an arrow drawn between two dots on a whiteboard:
    - ``edge_id`` is a unique label for this arrow
    - ``source_id`` is where the arrow starts (the "from" node)
    - ``target_id`` is where the arrow points (the "to" node)
    - ``rel_type`` is what the arrow means ("FRIENDS_WITH", "LIKES", etc.)
    - ``properties`` is extra info about the relationship

    Args:
        edge_id: A unique identifier for this edge.
        source_id: The ID of the node where this edge starts.
        target_id: The ID of the node where this edge ends.
        rel_type: The relationship type (e.g. "KNOWS", "WORKS_AT").
        properties: A dictionary of key-value attributes.

    """

    edge_id: str
    source_id: str
    target_id: str
    rel_type: str = ""
    properties: dict[str, object] = field(default_factory=lambda: {})

    def has_property(self, key: str) -> bool:
        """Check whether this edge has a given property key.

        Args:
            key: The property name to look for.

        Returns:
            True if the property exists, False otherwise.

        """
        return key in self.properties

    def get_property(self, key: str, default: object = None) -> object:
        """Get a property value by key, with an optional default.

        Args:
            key: The property name to retrieve.
            default: Value to return if the key is missing.

        Returns:
            The property value, or the default.

        """
        return self.properties.get(key, default)

    def set_property(self, key: str, value: object) -> None:
        """Set a property on this edge.

        Args:
            key: The property name.
            value: The property value.

        """
        self.properties[key] = value

    def remove_property(self, key: str) -> object:
        """Remove and return a property from this edge.

        Args:
            key: The property name to remove.

        Returns:
            The removed value.

        Raises:
            KeyError: If the property does not exist.

        """
        return self.properties.pop(key)

    def to_dict(self) -> dict[str, object]:
        """Write everything about this edge onto an index card.

        Like noting on a card who shook hands with whom, what kind of
        relationship it was, and when -- turns the edge into a plain
        dictionary you can save to a file.

        Returns:
            A dictionary representation of this edge.

        """
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "rel_type": self.rel_type,
            "properties": dict(self.properties),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Edge:
        """Rebuild an edge from the index card that to_dict wrote.

        Like reading a filed-away card and re-drawing that handshake
        (arrow) between two people -- turns a plain dictionary back into
        a real Edge.

        Args:
            data: A dictionary with edge fields.

        Returns:
            A new Edge instance.

        """
        edge_id = str(data.get("edge_id", ""))
        source_id = str(data.get("source_id", ""))
        target_id = str(data.get("target_id", ""))
        rel_type = str(data.get("rel_type", ""))
        raw_props = data.get("properties")
        props: dict[str, object] = {}
        if isinstance(raw_props, dict):
            for k, v in raw_props.items():  # pyright: ignore[reportUnknownVariableType]
                props[str(k)] = v  # pyright: ignore[reportUnknownArgumentType]
        return cls(
            edge_id=edge_id,
            source_id=source_id,
            target_id=target_id,
            rel_type=rel_type,
            properties=props,
        )
