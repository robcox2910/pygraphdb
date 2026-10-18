"""Model check -- Graph must behave exactly like two plain Python dicts.

A property test checks one rule for many inputs. A *model check* goes
further: Hypothesis invents a random *story* -- add this node, draw that
edge, remove the other node, ask who its neighbours are -- and plays it on
two things at once:

- the real ``Graph``;
- a **model**: a dict of nodes (id -> label and properties) and a dict of
  edges (id -> where it starts and ends, its type and properties), which
  we already trust to be right.

After every step the two must agree, and BFS and DFS from every node must
visit exactly the places the model says you can get to. If they ever
disagree, Hypothesis shrinks the story to the shortest list of steps that
still goes wrong.

The model is deliberately *not* a copy of ``Graph``'s code. ``Graph`` keeps
each node's own road lists so it never has to scan every edge; the model
just scans every edge, every time. That's slow, but it's obviously right,
so when the two disagree, the graph is the one to suspect.

See ``docs/property-testing.md`` for the walk-through.
"""

import unittest
from typing import cast

import pytest
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import (
    Bundle,
    MultipleResults,
    RuleBasedStateMachine,
    initialize,
    invariant,
    multiple,
    rule,
)

from pygraphdb.errors import (
    DuplicateEdgeError,
    DuplicateNodeError,
    EdgeNotFoundError,
    NodeNotFoundError,
)
from pygraphdb.graph import Graph
from pygraphdb.traversal import bfs, dfs
from tests.strategies import reachable_from

# Every story starts with these nodes. Random text hardly ever repeats, so
# with any ids at all most stories would be a few lonely nodes and no edges.
# (The property tests in test_properties.py try ids of every shape.)
FIRST_NODES = ["a", "b", "c", "d", "e"]

# What the dicts write down about one node, and about one edge.
type NodeNote = tuple[str, dict[str, object]]  # (label, properties)
type EdgeNote = tuple[str, str, str, dict[str, object]]  # (from, to, type, properties)


def node_names() -> st.SearchStrategy[str]:
    """Make one of the first node ids, or "f", which no story starts with."""
    return st.sampled_from([*FIRST_NODES, "f"])


def edge_names() -> st.SearchStrategy[str]:
    """Make any edge id: empty, spaces, emoji, accents, quotes, the lot."""
    return st.text(max_size=3)


def labels() -> st.SearchStrategy[str]:
    """Make any node label or relationship type, short."""
    return st.text(max_size=3)


def property_bags() -> st.SearchStrategy[dict[str, object]]:
    """Make a few properties, with keys "x" and "y" so updates overwrite as well as add."""
    return st.dictionaries(
        st.sampled_from(["x", "y"]), st.one_of(st.integers(), st.lists(st.integers())), max_size=2
    )


# --- The machine: one story, played on the graph and on two dicts -------------


class GraphMachine(RuleBasedStateMachine):
    """Play random adds, updates, removes and lookups on a Graph and on two dicts side by side."""

    # Bags of ids used earlier in the story, so later steps can join, read or
    # remove things that really are (or were) in the graph.
    nodes = Bundle("nodes")
    edges = Bundle("edges")

    def __init__(self) -> None:
        """Make an empty graph and two empty dicts (the first nodes go in just below)."""
        super().__init__()
        self.graph = Graph()
        self.node_notes: dict[str, NodeNote] = {}
        self.edge_notes: dict[str, EdgeNote] = {}

    @initialize(target=nodes)
    def add_the_first_nodes(self) -> MultipleResults[str]:
        """Start both with the same five nodes and no edges, and remember their ids."""
        for node_id in FIRST_NODES:
            self.graph.add_node(node_id)
            self.node_notes[node_id] = ("", {})
        return multiple(*FIRST_NODES)

    def roads(self) -> dict[str, set[str]]:
        """Return the model as a dict of sets: each node, and every node one edge away."""
        neighbours: dict[str, set[str]] = {node_id: set() for node_id in self.node_notes}
        for source, target, _, _ in self.edge_notes.values():
            neighbours[source].add(target)
        return neighbours

    @rule(target=nodes, node_id=node_names(), label=labels(), properties=property_bags())
    def add_node(self, node_id: str, label: str, properties: dict[str, object]) -> str:
        """Add a node to both, or get DuplicateNodeError if the id is taken; remember the id."""
        if node_id in self.node_notes:
            with pytest.raises(DuplicateNodeError):
                self.graph.add_node(node_id, label=label, properties=properties)
        else:
            assert (
                self.graph.add_node(node_id, label=label, properties=properties).node_id == node_id
            )
            self.node_notes[node_id] = (label, dict(properties))
        return node_id

    # Both ends come from the bag of used node ids, so most edges join real
    # nodes; an id whose node has since been removed tries a missing end.
    @rule(
        target=edges,
        edge_id=st.one_of(edges, edge_names()),
        source=nodes,
        destination=nodes,
        rel_type=labels(),
        properties=property_bags(),
    )
    def add_edge(
        self,
        edge_id: str,
        source: str,
        destination: str,
        rel_type: str,
        properties: dict[str, object],
    ) -> str:
        """Draw an edge in both, or get the right error if the id is taken or an end is missing."""
        if edge_id in self.edge_notes:
            with pytest.raises(DuplicateEdgeError):
                self.graph.add_edge(edge_id, source, destination)
        elif source not in self.node_notes or destination not in self.node_notes:
            with pytest.raises(NodeNotFoundError):
                self.graph.add_edge(edge_id, source, destination)
        else:
            edge = self.graph.add_edge(
                edge_id, source, destination, rel_type=rel_type, properties=properties
            )
            assert (edge.edge_id, edge.source_id, edge.target_id) == (edge_id, source, destination)
            self.edge_notes[edge_id] = (source, destination, rel_type, dict(properties))
        return edge_id

    @rule(node_id=st.one_of(nodes, node_names()), label=labels(), properties=property_bags())
    def update_node(self, node_id: str, label: str, properties: dict[str, object]) -> None:
        """Relabel a node and merge in some properties, or get NodeNotFoundError if it's not there."""
        if node_id not in self.node_notes:
            with pytest.raises(NodeNotFoundError):
                self.graph.update_node(node_id, label=label, properties=properties)
            return
        _, old_properties = self.node_notes[node_id]
        self.node_notes[node_id] = (label, {**old_properties, **properties})
        node = self.graph.update_node(node_id, label=label, properties=properties)
        assert (node.label, node.properties) == self.node_notes[node_id]

    @rule(edge_id=st.one_of(edges, edge_names()), rel_type=labels(), properties=property_bags())
    def update_edge(self, edge_id: str, rel_type: str, properties: dict[str, object]) -> None:
        """Retype an edge and merge in some properties, or get EdgeNotFoundError if it's not there."""
        if edge_id not in self.edge_notes:
            with pytest.raises(EdgeNotFoundError):
                self.graph.update_edge(edge_id, rel_type=rel_type, properties=properties)
            return
        source, target, _, old_properties = self.edge_notes[edge_id]
        self.edge_notes[edge_id] = (source, target, rel_type, {**old_properties, **properties})
        edge = self.graph.update_edge(edge_id, rel_type=rel_type, properties=properties)
        assert (edge.rel_type, edge.properties) == self.edge_notes[edge_id][2:]

    @rule(node_id=st.one_of(nodes, node_names()))
    def remove_node(self, node_id: str) -> None:
        """Remove a node, and every edge touching it, from both."""
        if node_id not in self.node_notes:
            with pytest.raises(NodeNotFoundError):
                self.graph.remove_node(node_id)
            return
        assert self.graph.remove_node(node_id).node_id == node_id
        del self.node_notes[node_id]
        self.edge_notes = {
            edge_id: note
            for edge_id, note in self.edge_notes.items()
            if node_id not in (note[0], note[1])
        }

    @rule(edge_id=st.one_of(edges, edge_names()))
    def remove_edge(self, edge_id: str) -> None:
        """Remove an edge from both, or get EdgeNotFoundError if it isn't there."""
        if edge_id not in self.edge_notes:
            with pytest.raises(EdgeNotFoundError):
                self.graph.remove_edge(edge_id)
            return
        assert self.graph.remove_edge(edge_id).edge_id == edge_id
        del self.edge_notes[edge_id]

    @rule(node_id=st.one_of(nodes, node_names()))
    def look_at_node(self, node_id: str) -> None:
        """Read a node: its label and properties, or NodeNotFoundError from every lookup."""
        assert self.graph.has_node(node_id) == (node_id in self.node_notes)
        if node_id in self.node_notes:
            node = self.graph.get_node(node_id)
            assert (node.label, node.properties) == self.node_notes[node_id]
            return
        for lookup in (
            self.graph.get_node,
            self.graph.get_neighbors,
            self.graph.get_outgoing_edges,
            self.graph.get_incoming_edges,
            self.graph.out_degree,
            self.graph.in_degree,
            self.graph.degree,
        ):
            with pytest.raises(NodeNotFoundError):
                lookup(node_id)
        for traverse in (bfs, dfs):
            with pytest.raises(NodeNotFoundError):
                traverse(self.graph, node_id)

    @rule(edge_id=st.one_of(edges, edge_names()))
    def look_at_edge(self, edge_id: str) -> None:
        """Read an edge: its ends, type and properties, or EdgeNotFoundError if it isn't there."""
        assert self.graph.has_edge(edge_id) == (edge_id in self.edge_notes)
        if edge_id not in self.edge_notes:
            with pytest.raises(EdgeNotFoundError):
                self.graph.get_edge(edge_id)
            return
        edge = self.graph.get_edge(edge_id)
        assert (edge.source_id, edge.target_id, edge.rel_type, edge.properties) == (
            self.edge_notes[edge_id]
        )

    @invariant()
    def same_nodes_and_edges(self) -> None:
        """After every step, the graph holds exactly the dicts' nodes and edges."""
        assert self.graph.node_count == len(self.node_notes)
        assert self.graph.edge_count == len(self.edge_notes)
        assert {
            n.node_id: (n.label, n.properties) for n in self.graph.get_all_nodes()
        } == self.node_notes
        assert {
            e.edge_id: (e.source_id, e.target_id, e.rel_type, e.properties)
            for e in self.graph.get_all_edges()
        } == self.edge_notes

    @invariant()
    def every_node_has_the_right_roads(self) -> None:
        """After every step, each node's edges, degrees and neighbours match the dicts."""
        for node_id in self.node_notes:
            leaving = {e for e, note in self.edge_notes.items() if note[0] == node_id}
            arriving = {e for e, note in self.edge_notes.items() if note[1] == node_id}
            assert {e.edge_id for e in self.graph.get_outgoing_edges(node_id)} == leaving
            assert {e.edge_id for e in self.graph.get_incoming_edges(node_id)} == arriving
            assert self.graph.out_degree(node_id) == len(leaving)
            assert self.graph.in_degree(node_id) == len(arriving)
            assert self.graph.degree(node_id) == len(leaving) + len(arriving)
            outward = {self.edge_notes[e][1] for e in leaving}
            inward = {self.edge_notes[e][0] for e in arriving}
            for direction, expected in [
                ("outgoing", outward),
                ("incoming", inward),
                ("both", outward | inward),
            ]:
                found = [n.node_id for n in self.graph.get_neighbors(node_id, direction=direction)]
                assert len(found) == len(set(found))  # each neighbour once
                assert set(found) == expected

    @invariant()
    def traversals_reach_exactly_the_reachable_nodes(self) -> None:
        """After every step, BFS and DFS from every node visit exactly what the dicts can reach."""
        roads = self.roads()
        for start in self.node_notes:
            expected = reachable_from(roads, start)
            for traverse in (bfs, dfs):
                visited = [node.node_id for node in traverse(self.graph, start)]
                assert len(visited) == len(set(visited))  # each node once
                assert set(visited) == expected


# why: 20 steps find the same bugs; 50 (the default) is most of the run time
GraphMachine.TestCase.settings = settings(stateful_step_count=20)
# pytest runs this like any other test class: one run plays 100 random stories.
# (Hypothesis doesn't say what type ``TestCase`` is, so ``cast`` tells pyright.)
TestGraphModel = cast("type[unittest.TestCase]", GraphMachine.TestCase)
