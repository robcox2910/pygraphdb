"""Property-based tests -- rules that must hold for *every* input.

An ordinary test checks one example someone thought of: "on the map
a -> b -> c -> d, BFS from ``a`` visits a, b, c, d". A property test states
a rule instead, such as "BFS visits exactly the places you can get to, each
once", and lets Hypothesis invent hundreds of maps to try to break it. If
one breaks the rule, Hypothesis *shrinks* it down to the smallest map that
still fails, and shows you that.

Each test below says its rule in plain English in its docstring. The
strategies at the top are recipes for making random inputs; each one is
named for what it makes.

The step-by-step check of ``Graph`` against a plain dict of sets lives in
``tests/test_model.py``. See ``docs/property-testing.md`` for the walk-through.
"""

import json
import tempfile
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from pygraphdb.errors import PersistenceError
from pygraphdb.graph import Graph
from pygraphdb.pathfinding import shortest_path
from pygraphdb.persistence import load_graph, save_graph
from pygraphdb.traversal import bfs, dfs
from tests.strategies import RoadMap, reachable_from, road_maps, steps_from

# --- Strategies: recipes for random inputs -----------------------------------
# place_names() and road_maps() live in tests/strategies.py, shared with the
# model check.

# A nested value is built from at most this many plain pieces. Small values
# find the same bugs, and a failure shrinks to a small value anyway.
MOST_PIECES_PER_VALUE = 3


def json_values() -> st.SearchStrategy[object]:
    """Make any value JSON can hold: text, numbers, True/False, None, lists and dicts."""
    plain = st.one_of(
        st.none(),
        st.booleans(),
        st.integers(),
        # NaN ("not a number") is never equal to itself, so ``==`` could never
        # confirm it came back. That's a rule of floats, not of PyGraphDB.
        st.floats(allow_nan=False),
        st.text(),
    )
    return st.recursive(plain, lists_and_dicts_of, max_leaves=MOST_PIECES_PER_VALUE)


def lists_and_dicts_of(children: st.SearchStrategy[object]) -> st.SearchStrategy[object]:
    """Make a list, or a dict with text keys, holding values made by ``children``."""
    return st.one_of(st.lists(children), st.dictionaries(st.text(), children))


def property_bags() -> st.SearchStrategy[dict[str, object]]:
    """Make the properties of one node or edge: any text keys, any JSON values."""
    # Save files are JSON (docs/concepts/persistence.md), so properties are
    # JSON values: a tuple or a date would come back as a list or a string.
    return st.dictionaries(st.text(), json_values(), max_size=2)


def exactly[T](count: int, items: st.SearchStrategy[T]) -> st.SearchStrategy[list[T]]:
    """Make a list of exactly ``count`` things, each made by ``items``."""
    return st.lists(items, min_size=count, max_size=count)


@dataclass(frozen=True)
class GraphPlan:
    """Everything one graph holds, written out plainly so a failing example is easy to read."""

    nodes: list[tuple[str, str, dict[str, object]]]  # (id, label, properties)
    edges: list[tuple[str, str, str, str, dict[str, object]]]  # (id, from, to, type, properties)

    def build(self) -> Graph:
        """Return a new Graph holding exactly these nodes and edges."""
        graph = Graph()
        for node_id, label, properties in self.nodes:
            graph.add_node(node_id, label=label, properties=properties)
        for edge_id, source, target, rel_type, properties in self.edges:
            graph.add_edge(edge_id, source, target, rel_type=rel_type, properties=properties)
        return graph


@st.composite
def graph_plans(draw: st.DrawFn) -> GraphPlan:
    """Make a whole graph's plan: a random road map, with labels, types and properties everywhere."""
    road_map = draw(road_maps())
    places, roads = len(road_map.places), len(road_map.roads)
    labels = draw(exactly(places, st.text()))
    node_properties = draw(exactly(places, property_bags()))
    # Each edge needs its own id: add_edge refuses one that's taken.
    edge_ids = draw(st.lists(st.text(), min_size=roads, max_size=roads, unique=True))
    rel_types = draw(exactly(roads, st.text()))
    edge_properties = draw(exactly(roads, property_bags()))
    nodes = list(zip(road_map.places, labels, node_properties, strict=True))
    edges = [
        (edge_id, source, target, rel_type, properties)
        for edge_id, (source, target), rel_type, properties in zip(
            edge_ids, road_map.roads, rel_types, edge_properties, strict=True
        )
    ]
    return GraphPlan(nodes=nodes, edges=edges)


def any_bytes() -> st.SearchStrategy[bytes]:
    """Make any run of raw bytes, including the empty one and ones that aren't text."""
    return st.binary()


def short_names() -> st.SearchStrategy[str]:
    """Make one of two ids, "a" or "b", so ids clash and edges can join real nodes."""
    return st.sampled_from(["a", "b"])


def node_cards() -> st.SearchStrategy[dict[str, object]]:
    """Make one node "card" for a save file: any of its fields, holding short ids or any JSON."""
    return st.fixed_dictionaries(
        {}, optional={"node_id": short_names(), "label": json_values(), "properties": json_values()}
    )


def edge_cards() -> st.SearchStrategy[dict[str, object]]:
    """Make one edge "card" for a save file: any of its fields, holding short ids or any JSON."""
    return st.fixed_dictionaries(
        {},
        optional={
            "edge_id": short_names(),
            "source_id": short_names(),
            "target_id": short_names(),
            "rel_type": json_values(),
            "properties": json_values(),
        },
    )


def any_json() -> st.SearchStrategy[object]:
    """Make any JSON document: some random, some shaped like a save file with odd insides."""
    looks_like_a_save_file = st.fixed_dictionaries(
        {"nodes": st.lists(node_cards()), "edges": st.lists(edge_cards())}
    )
    return st.one_of(json_values(), looks_like_a_save_file)


# --- Helpers -----------------------------------------------------------------


def graph_of(road_map: RoadMap) -> Graph:
    """Return a Graph with a node for every place and an edge for every road."""
    graph = Graph()
    for place in road_map.places:
        graph.add_node(place)
    for number, (source, target) in enumerate(road_map.roads):
        graph.add_edge(f"road {number}", source, target)
    return graph


def load_or_refuse(path: Path) -> Graph | None:
    """Load the graph at ``path``, accepting only a PersistenceError refusal.

    A PersistenceError is caught and turned into ``None``: refusing a bad
    file is fine. Any *other* exception escapes and fails the test, and that
    is the whole check.
    """
    try:
        return load_graph(path)
    except PersistenceError:
        return None


# --- Traversal: exactly the places you can get to -----------------------------


@given(road_map=road_maps())
def test_bfs_visits_exactly_the_reachable_places(road_map: RoadMap) -> None:
    """From any start, BFS visits every place you can get to, each once, and nowhere else."""
    graph = graph_of(road_map)
    for start in road_map.places:
        visited = [node.node_id for node in bfs(graph, start)]
        assert visited[0] == start
        assert len(visited) == len(set(visited))
        assert set(visited) == reachable_from(road_map.roads_from(), start)


@given(road_map=road_maps())
def test_dfs_visits_exactly_the_reachable_places(road_map: RoadMap) -> None:
    """From any start, DFS visits every place you can get to, each once, and nowhere else."""
    graph = graph_of(road_map)
    for start in road_map.places:
        visited = [node.node_id for node in dfs(graph, start)]
        assert visited[0] == start
        assert len(visited) == len(set(visited))
        assert set(visited) == reachable_from(road_map.roads_from(), start)


@given(road_map=road_maps())
def test_bfs_visits_nearer_places_first(road_map: RoadMap) -> None:
    """BFS spreads like ripples: it never visits a place before one that is fewer roads away."""
    graph = graph_of(road_map)
    for start in road_map.places:
        steps = steps_from(road_map.roads_from(), start)
        distances = [steps[node.node_id] for node in bfs(graph, start)]
        assert distances == sorted(distances)


@given(road_map=road_maps())
def test_shortest_path_takes_the_fewest_roads(road_map: RoadMap) -> None:
    """A shortest path follows real roads and takes the fewest; no path means unreachable."""
    graph = graph_of(road_map)
    neighbours = road_map.roads_from()
    for start in road_map.places:
        steps = steps_from(neighbours, start)
        for end in road_map.places:
            path = [node.node_id for node in shortest_path(graph, start, end)]
            if end not in steps:
                assert path == []
                continue
            assert path[0] == start
            assert path[-1] == end
            assert len(path) - 1 == steps[end]
            assert all(there in neighbours[here] for here, there in pairwise(path))


# --- Save and load: whatever you save comes back -----------------------------


@given(plan=graph_plans())
def test_save_then_load_gives_back_the_same_graph(plan: GraphPlan) -> None:
    """Loading a saved graph gives back the same nodes and edges, with the same types inside."""
    graph = plan.build()
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "graph.json"
        save_graph(graph, path)
        loaded = load_graph(path).to_dict()
    assert loaded == graph.to_dict()
    # ``==`` thinks True == 1 == 1.0, even inside lists and dicts, so a graph
    # that loaded a property ``[True]`` as ``[1]`` would pass it. ``repr``
    # writes True as ``True`` and 1.0 as ``1.0``, so it checks every type too.
    assert repr(loaded) == repr(graph.to_dict())


# --- Loading junk: a bad save file is refused, never a crash ------------------


@given(junk=any_bytes())
def test_any_bytes_on_disk_load_or_raise_persistence_error(junk: bytes) -> None:
    """Whatever bytes are in the file, loading gives a graph or a PersistenceError, never another error."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "graph.json"
        path.write_bytes(junk)
        load_or_refuse(path)


@given(document=any_json())
def test_any_json_on_disk_load_or_raise_persistence_error(document: object) -> None:
    """Whatever JSON is in the file, loading gives a graph or a PersistenceError, never another error."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "graph.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        load_or_refuse(path)


@given(document=any_json())
def test_a_loaded_graph_agrees_with_itself(document: object) -> None:
    """Whatever file loads, every edge a node lists really starts or ends there, and none is counted twice."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "graph.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        graph = load_or_refuse(path)
    if graph is None:
        return
    for node in graph.get_all_nodes():
        assert all(
            edge.source_id == node.node_id for edge in graph.get_outgoing_edges(node.node_id)
        )
        assert all(
            edge.target_id == node.node_id for edge in graph.get_incoming_edges(node.node_id)
        )
    assert sum(graph.out_degree(node.node_id) for node in graph.get_all_nodes()) == graph.edge_count
