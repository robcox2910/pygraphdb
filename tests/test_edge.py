"""Test the Edge dataclass."""

import pytest

from pygraphdb.edge import Edge


class TestEdgeCreation:
    """Test creating edges with various configurations."""

    def test_create_edge_with_all_fields(self) -> None:
        """Create an edge with all fields specified."""
        edge = Edge(
            edge_id="e1",
            source_id="1",
            target_id="2",
            rel_type="KNOWS",
            properties={"since": 2024},
        )
        assert edge.edge_id == "e1"
        assert edge.source_id == "1"
        assert edge.target_id == "2"
        assert edge.rel_type == "KNOWS"
        expected_year = 2024
        assert edge.properties["since"] == expected_year

    def test_create_edge_with_defaults(self) -> None:
        """Create an edge with minimal fields (defaults for type and props)."""
        edge = Edge(edge_id="e1", source_id="1", target_id="2")
        assert edge.rel_type == ""
        assert edge.properties == {}


class TestEdgeProperties:
    """Test edge property operations."""

    def test_has_property(self) -> None:
        """Check has_property for existing and missing keys."""
        edge = Edge(edge_id="e1", source_id="1", target_id="2", properties={"weight": 5})
        assert edge.has_property("weight")
        assert not edge.has_property("color")

    def test_get_property(self) -> None:
        """Get property values with defaults."""
        expected_weight = 5
        edge = Edge(
            edge_id="e1", source_id="1", target_id="2", properties={"weight": expected_weight}
        )
        assert edge.get_property("weight") == expected_weight
        assert edge.get_property("color", "red") == "red"

    def test_set_property(self) -> None:
        """Set a new property on an edge."""
        edge = Edge(edge_id="e1", source_id="1", target_id="2")
        expected_weight = 10
        edge.set_property("weight", expected_weight)
        assert edge.properties["weight"] == expected_weight

    def test_remove_property(self) -> None:
        """Remove a property from an edge."""
        expected_weight = 5
        edge = Edge(
            edge_id="e1", source_id="1", target_id="2", properties={"weight": expected_weight}
        )
        removed = edge.remove_property("weight")
        assert removed == expected_weight
        assert "weight" not in edge.properties

    def test_remove_missing_property_raises(self) -> None:
        """Remove a missing property raises KeyError."""
        edge = Edge(edge_id="e1", source_id="1", target_id="2")
        with pytest.raises(KeyError):
            edge.remove_property("weight")


class TestEdgeSerialization:
    """Test edge serialization to/from dictionaries."""

    def test_to_dict(self) -> None:
        """Serialize an edge to a dictionary."""
        edge = Edge(
            edge_id="e1",
            source_id="1",
            target_id="2",
            rel_type="KNOWS",
            properties={"since": 2024},
        )
        data = edge.to_dict()
        assert data["edge_id"] == "e1"
        assert data["source_id"] == "1"
        assert data["target_id"] == "2"
        assert data["rel_type"] == "KNOWS"

    def test_from_dict(self) -> None:
        """Deserialize an edge from a dictionary."""
        data: dict[str, object] = {
            "edge_id": "e1",
            "source_id": "1",
            "target_id": "2",
            "rel_type": "LIKES",
            "properties": {"weight": 3},
        }
        edge = Edge.from_dict(data)
        assert edge.edge_id == "e1"
        assert edge.rel_type == "LIKES"

    def test_round_trip(self) -> None:
        """Serialize then deserialize preserves all data."""
        original = Edge(
            edge_id="e1",
            source_id="a",
            target_id="b",
            rel_type="WORKS_AT",
            properties={"role": "engineer"},
        )
        restored = Edge.from_dict(original.to_dict())
        assert restored.edge_id == original.edge_id
        assert restored.source_id == original.source_id
        assert restored.target_id == original.target_id
        assert restored.rel_type == original.rel_type
        assert restored.properties == original.properties
