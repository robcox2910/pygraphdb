"""Model check -- Graph must behave exactly like two plain Python dicts.

A property test checks one rule for many inputs. A *model check* goes
further: Hypothesis invents a random *story* -- add this node, draw that
edge, remove the other node, ask who its neighbours are -- and plays it on
two things at once:

- the real ``Graph``;
- a **model**: a dict of nodes (id -> label) and a dict of edges
  (id -> where it starts and ends), which we already trust to be right.

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


def node_names() -> st.SearchStrategy[str]:
    """Make one of the first node ids, or "f", which no story starts with."""
    return st.sampled_from([*FIRST_NODES, "f"])


def edge_names() -> st.SearchStrategy[str]:
    """Make any edge id: empty, spaces, emoji, accents, quotes, the lot."""
    return st.text(max_size=3)


def labels() -> st.SearchStrategy[str]:
    """Make any node label, short."""
    return st.text(max_size=3)


# --- The machine: one story, played on the graph and on two dicts -------------


class GraphMachine(RuleBasedStateMachine):
    """Play random adds, removes and lookups on a Graph and on two dicts side by side."""

    # Bags of ids used earlier in the story, so later steps can join, read or
    # remove things that really are (or were) in the graph.
    nodes = Bundle("nodes")
    edges = Bundle("edges")

    def __init__(self) -> None:
        """Make an empty graph and two empty dicts (the first nodes go in just below)."""
        super().__init__()
        self.graph = Graph()
        self.labels: dict[str, str] = {}
        self.ends: dict[str, tuple[str, str]] = {}

    @initialize(target=nodes)
    def add_the_first_nodes(self) -> MultipleResults[str]:
        """Start both with the same five nodes and no edges, and remember their ids."""
        for node_id in FIRST_NODES:
            self.graph.add_node(node_id)
            self.labels[node_id] = ""
        return multiple(*FIRST_NODES)

    def roads(self) -> dict[str, set[str]]:
        """Return the model as a dict of sets: each node, and every node one edge away."""
        neighbours: dict[str, set[str]] = {node_id: set() for node_id in self.labels}
        for source, target in self.ends.values():
            neighbours[source].add(target)
        return neighbours

    @rule(target=nodes, node_id=node_names(), label=labels())
    def add_node(self, node_id: str, label: str) -> str:
        """Add a node to both, or get DuplicateNodeError if the id is taken; remember the id."""
        if node_id in self.labels:
            with pytest.raises(DuplicateNodeError):
                self.graph.add_node(node_id, label=label)
        else:
            assert self.graph.add_node(node_id, label=label).node_id == node_id
            self.labels[node_id] = label
        return node_id

    # Both ends come from the bag of used node ids, so most edges join real
    # nodes; an id whose node has since been removed tries a missing end.
    @rule(target=edges, edge_id=st.one_of(edges, edge_names()), source=nodes, destination=nodes)
    def add_edge(self, edge_id: str, source: str, destination: str) -> str:
        """Draw an edge in both, or get the right error if the id is taken or an end is missing."""
        if edge_id in self.ends:
            with pytest.raises(DuplicateEdgeError):
                self.graph.add_edge(edge_id, source, destination)
        elif source not in self.labels or destination not in self.labels:
            with pytest.raises(NodeNotFoundError):
                self.graph.add_edge(edge_id, source, destination)
        else:
            self.graph.add_edge(edge_id, source, destination)
            self.ends[edge_id] = (source, destination)
        return edge_id

    @rule(node_id=st.one_of(nodes, node_names()), label=labels())
    def relabel_node(self, node_id: str, label: str) -> None:
        """Give a node a new label in both, or get NodeNotFoundError if it isn't there."""
        if node_id not in self.labels:
            with pytest.raises(NodeNotFoundError):
                self.graph.update_node(node_id, label=label)
            return
        self.graph.update_node(node_id, label=label)
        self.labels[node_id] = label

    @rule(node_id=st.one_of(nodes, node_names()))
    def remove_node(self, node_id: str) -> None:
        """Remove a node, and every edge touching it, from both."""
        if node_id not in self.labels:
            with pytest.raises(NodeNotFoundError):
                self.graph.remove_node(node_id)
            return
        assert self.graph.remove_node(node_id).node_id == node_id
        del self.labels[node_id]
        self.ends = {
            edge_id: (source, target)
            for edge_id, (source, target) in self.ends.items()
            if node_id not in (source, target)
        }

    @rule(edge_id=st.one_of(edges, edge_names()))
    def remove_edge(self, edge_id: str) -> None:
        """Remove an edge from both, or get EdgeNotFoundError if it isn't there."""
        if edge_id not in self.ends:
            with pytest.raises(EdgeNotFoundError):
                self.graph.remove_edge(edge_id)
            return
        assert self.graph.remove_edge(edge_id).edge_id == edge_id
        del self.ends[edge_id]

    @rule(node_id=st.one_of(nodes, node_names()))
    def look_at_node(self, node_id: str) -> None:
        """Read a node: its label, or NodeNotFoundError (from BFS and DFS too) if it isn't there."""
        assert self.graph.has_node(node_id) == (node_id in self.labels)
        if node_id not in self.labels:
            with pytest.raises(NodeNotFoundError):
                self.graph.get_node(node_id)
            with pytest.raises(NodeNotFoundError):
                self.graph.get_neighbors(node_id)
            with pytest.raises(NodeNotFoundError):
                bfs(self.graph, node_id)
            with pytest.raises(NodeNotFoundError):
                dfs(self.graph, node_id)
            return
        assert self.graph.get_node(node_id).label == self.labels[node_id]

    @rule(edge_id=st.one_of(edges, edge_names()))
    def look_at_edge(self, edge_id: str) -> None:
        """Read an edge: where it starts and ends, or EdgeNotFoundError if it isn't there."""
        assert self.graph.has_edge(edge_id) == (edge_id in self.ends)
        if edge_id not in self.ends:
            with pytest.raises(EdgeNotFoundError):
                self.graph.get_edge(edge_id)
            return
        edge = self.graph.get_edge(edge_id)
        assert (edge.source_id, edge.target_id) == self.ends[edge_id]

    @invariant()
    def same_nodes_and_edges(self) -> None:
        """After every step, the graph holds exactly the dicts' nodes and edges."""
        assert self.graph.node_count == len(self.labels)
        assert self.graph.edge_count == len(self.ends)
        assert {n.node_id: n.label for n in self.graph.get_all_nodes()} == self.labels
        assert {e.edge_id: (e.source_id, e.target_id) for e in self.graph.get_all_edges()} == (
            self.ends
        )

    @invariant()
    def every_node_has_the_right_roads(self) -> None:
        """After every step, each node's edges, degrees and neighbours match the dicts."""
        for node_id in self.labels:
            leaving = {e for e, (source, _) in self.ends.items() if source == node_id}
            arriving = {e for e, (_, target) in self.ends.items() if target == node_id}
            assert {e.edge_id for e in self.graph.get_outgoing_edges(node_id)} == leaving
            assert {e.edge_id for e in self.graph.get_incoming_edges(node_id)} == arriving
            assert self.graph.out_degree(node_id) == len(leaving)
            assert self.graph.in_degree(node_id) == len(arriving)
            assert self.graph.degree(node_id) == len(leaving) + len(arriving)
            outward = {self.ends[e][1] for e in leaving}
            inward = {self.ends[e][0] for e in arriving}
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
        for start in self.labels:
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
