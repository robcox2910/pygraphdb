"""Test the Node dataclass."""

import pytest

from pygraphdb.node import Node


class TestNodeCreation:
    """Test creating nodes with various configurations."""

    def test_create_node_with_all_fields(self) -> None:
        """Create a node with an ID, label, and properties."""
        node = Node(node_id="1", label="Person", properties={"name": "Alice"})
        assert node.node_id == "1"
        assert node.label == "Person"
        assert node.properties == {"name": "Alice"}

    def test_create_node_with_defaults(self) -> None:
        """Create a node with only an ID (defaults for label and properties)."""
        node = Node(node_id="1")
        assert node.node_id == "1"
        assert node.label == ""
        assert node.properties == {}

    def test_create_node_with_multiple_properties(self) -> None:
        """Create a node with several properties."""
        expected_age = 13
        props: dict[str, object] = {"name": "Alice", "age": expected_age, "active": True}
        node = Node(node_id="1", label="Person", properties=props)
        assert len(node.properties) == 3  # noqa: PLR2004


class TestNodeProperties:
    """Test node property operations."""

    def test_has_property_true(self) -> None:
        """Check that has_property returns True for existing keys."""
        node = Node(node_id="1", properties={"name": "Alice"})
        assert node.has_property("name")

    def test_has_property_false(self) -> None:
        """Check that has_property returns False for missing keys."""
        node = Node(node_id="1")
        assert not node.has_property("name")

    def test_get_property_existing(self) -> None:
        """Get an existing property value."""
        node = Node(node_id="1", properties={"name": "Alice"})
        assert node.get_property("name") == "Alice"

    def test_get_property_missing_with_default(self) -> None:
        """Get a missing property returns the default value."""
        node = Node(node_id="1")
        assert node.get_property("name", "Unknown") == "Unknown"

    def test_get_property_missing_default_none(self) -> None:
        """Get a missing property returns None by default."""
        node = Node(node_id="1")
        assert node.get_property("name") is None

    def test_set_property(self) -> None:
        """Set a new property on a node."""
        node = Node(node_id="1")
        node.set_property("name", "Alice")
        assert node.properties["name"] == "Alice"

    def test_set_property_overwrites(self) -> None:
        """Set an existing property overwrites the old value."""
        node = Node(node_id="1", properties={"name": "Alice"})
        node.set_property("name", "Bob")
        assert node.properties["name"] == "Bob"

    def test_remove_property(self) -> None:
        """Remove a property from a node."""
        node = Node(node_id="1", properties={"name": "Alice"})
        removed = node.remove_property("name")
        assert removed == "Alice"
        assert "name" not in node.properties

    def test_remove_property_missing_raises(self) -> None:
        """Remove a missing property raises KeyError."""
        node = Node(node_id="1")
        with pytest.raises(KeyError):
            node.remove_property("name")


class TestNodeSerialization:
    """Test node serialization to/from dictionaries."""

    def test_to_dict(self) -> None:
        """Serialize a node to a dictionary."""
        node = Node(node_id="1", label="Person", properties={"name": "Alice"})
        data = node.to_dict()
        assert data["node_id"] == "1"
        assert data["label"] == "Person"
        assert data["properties"] == {"name": "Alice"}

    def test_from_dict(self) -> None:
        """Deserialize a node from a dictionary."""
        data: dict[str, object] = {
            "node_id": "1",
            "label": "Person",
            "properties": {"name": "Alice"},
        }
        node = Node.from_dict(data)
        assert node.node_id == "1"
        assert node.label == "Person"
        assert node.properties == {"name": "Alice"}

    def test_round_trip(self) -> None:
        """Serialize then deserialize preserves all data."""
        original = Node(node_id="1", label="City", properties={"name": "London", "pop": 9000000})
        restored = Node.from_dict(original.to_dict())
        assert restored.node_id == original.node_id
        assert restored.label == original.label
        assert restored.properties == original.properties
