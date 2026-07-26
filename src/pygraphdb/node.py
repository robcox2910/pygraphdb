"""Node -- a single entity in a graph database.

Imagine a party where every guest wears a name tag. Each person (node)
has a unique ID (like their phone number), a label (like "Student" or
"Teacher"), and properties (like their name, age, or favorite color).

A node is the building block of a graph. By itself it's just a dot on
a whiteboard -- but connect it to other nodes with edges, and suddenly
you have a map of relationships!

Example:
    >>> from pygraphdb.node import Node
    >>> alice = Node(node_id="1", label="Person", properties={"name": "Alice", "age": 13})
    >>> alice.label
    'Person'
    >>> alice.properties["name"]
    'Alice'

"""

from dataclasses import dataclass, field


@dataclass
class Node:
    """A single entity in the graph with an ID, label, and properties.

    Think of a node like a person at a party:
    - ``node_id`` is their unique wristband number (no two people share one)
    - ``label`` is the group they belong to ("Student", "Teacher", "Parent")
    - ``properties`` is everything about them (name, age, hobbies)

    Args:
        node_id: A unique identifier for this node.
        label: A category or type label (e.g. "Person", "City").
        properties: A dictionary of key-value attributes.

    """

    node_id: str
    label: str = ""
    properties: dict[str, object] = field(default_factory=lambda: {})

    def has_property(self, key: str) -> bool:
        """Check whether this node has a given property key.

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
        """Set a property on this node.

        Args:
            key: The property name.
            value: The property value.

        """
        self.properties[key] = value

    def remove_property(self, key: str) -> object:
        """Remove and return a property from this node.

        Args:
            key: The property name to remove.

        Returns:
            The removed value.

        Raises:
            KeyError: If the property does not exist.

        """
        return self.properties.pop(key)

    def to_dict(self) -> dict[str, object]:
        """Write everything about this node onto an index card.

        Like copying a party guest's wristband number, group, and details
        onto a card you can file away -- turns the node into a plain
        dictionary you can save to a file.

        Returns:
            A dictionary representation of this node.

        """
        return {
            "node_id": self.node_id,
            "label": self.label,
            "properties": dict(self.properties),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Node:
        """Rebuild a node from the index card that to_dict wrote.

        Like reading a filed-away card and bringing that party guest back --
        turns a plain dictionary back into a real Node.

        Args:
            data: A dictionary with node_id, label, and properties keys.

        Returns:
            A new Node instance.

        """
        node_id = str(data.get("node_id", ""))
        label = str(data.get("label", ""))
        raw_props = data.get("properties")
        props: dict[str, object] = {}
        if isinstance(raw_props, dict):
            for k, v in raw_props.items():  # pyright: ignore[reportUnknownVariableType]
                props[str(k)] = v  # pyright: ignore[reportUnknownArgumentType]
        return cls(node_id=node_id, label=label, properties=props)
