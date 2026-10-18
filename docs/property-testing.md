# Property Testing (Every Reachable Place, Exactly Once)

## The Town Surveyor

Picture a town of one-way streets. A graph is the town: nodes are the
places, and edges are the one-way roads. PyGraphDB's `bfs`
([breadth-first search](concepts/traversal.md)) explores it: it starts at
one house and follows the streets, visiting every place it can get to.

How would you check `bfs` works? The usual way: draw one little town
(`a -> b -> c -> d`), run `bfs` from `a`, and check it visits
`a, b, c, d`. That's an **example test**. It's useful, but it only tells
you about the one town you thought of.

Now imagine a surveyor. All day long they draw thousands of tiny random
towns -- one house on its own, a road that loops straight back to where it
started, two roads between the same two houses, places with names like
`""` or `"🍕"` -- and for each town they check a single rule:

> From any starting place, BFS visits every place you can get to,
> each one once, and nowhere else.

That rule is a **property**. It doesn't say what any one town looks like.
It says something that must be true for *every* town.

When the surveyor finds a town that breaks the rule, they don't just
report "something went wrong in a town with 40 roads". They rub out
houses and roads one at a time, checking it still goes wrong each time,
until the town is as small as it can be. That rubbing-out is called
**shrinking**, and it's the best part: the smallest failing town usually
points straight at the bug.

In Python, the surveyor is a library called
[Hypothesis](https://hypothesis.readthedocs.io/). PyGraphDB's property
tests live in `tests/test_properties.py`, next to the ordinary example
tests, and the model check (more on that below) is in `tests/test_model.py`.

## A Property from PyGraphDB

Here's the surveyor's rule for BFS, with the recipes it uses (the first
four live in `tests/strategies.py`, shared with the model check):

```python
@dataclass(frozen=True)
class RoadMap:
    """A plain description of a graph: some places, and one-way roads between them."""

    places: list[str]
    roads: list[tuple[str, str]]

    def roads_from(self) -> dict[str, set[str]]:
        """Return the map as a dict of sets: each place, and every place one road away."""
        neighbours: dict[str, set[str]] = {place: set() for place in self.places}
        for source, target in self.roads:
            neighbours[source].add(target)
        return neighbours


def place_names() -> st.SearchStrategy[str]:
    """Make any node id: empty, spaces, emoji, accents, quotes, the lot."""
    return st.text(max_size=3)


@st.composite
def road_maps(draw: st.DrawFn) -> RoadMap:
    """Make a road map: one to five places, and up to eight one-way roads between them."""
    places = draw(st.lists(place_names(), min_size=1, max_size=MOST_PLACES, unique=True))
    one_place = st.sampled_from(places)
    roads = draw(st.lists(st.tuples(one_place, one_place), max_size=MOST_ROADS))
    return RoadMap(places=places, roads=roads)


def reachable_from(neighbours: dict[str, set[str]], start: str) -> set[str]:
    """Return every place you can get to from ``start``, worked out the slow, obvious way."""
    reached = {start}
    while True:
        one_more_road = {place for here in reached for place in neighbours[here]}
        if one_more_road <= reached:
            return reached
        reached |= one_more_road


@given(road_map=road_maps())
def test_bfs_visits_exactly_the_reachable_places(road_map: RoadMap) -> None:
    """From any start, BFS visits every place you can get to, each once, and nowhere else."""
    graph = graph_of(road_map)
    for start in road_map.places:
        visited = [node.node_id for node in bfs(graph, start)]
        assert visited[0] == start
        assert len(visited) == len(set(visited))
        assert set(visited) == reachable_from(road_map.roads_from(), start)
```

Line by line:

- **`RoadMap`** is a town written out as plainly as possible: a list of
  places and a list of `(from, to)` roads. `roads_from()` turns it into a
  **dict of sets** -- each place, and the set of places one road away.
  When a test fails, Hypothesis prints the `RoadMap`, so you can read the
  town at a glance.
- **`place_names()` and `road_maps()`** are **strategies**: recipes for
  making random inputs. `st.text(max_size=3)` makes any short string,
  including `""`, `" "` and `"Zoë"`. `road_maps()` is a `@st.composite`
  recipe: it draws some places first, then draws roads that only use
  those places, so every road joins two real places. Roads can loop back
  to where they started, and two roads can join the same pair of places.
- **`reachable_from()`** is the surveyor's own slow, obvious answer. Start
  with just `start`; keep adding every place one more road away; stop when
  nothing new turns up. No queue, no visited list -- nothing borrowed from
  PyGraphDB's BFS.
- **`@given(road_map=road_maps())`** tells Hypothesis to run the test many
  times (100 in a normal run), each time with a fresh random town.
- **The docstring** says the rule in plain English. If you can't say the
  rule in one sentence, it probably isn't a good property yet.
- **`graph_of(road_map)`** is a small helper that builds a real `Graph`
  with `add_node` and `add_edge`.
- **The loop** runs BFS from *every* place in the town, not just one.
- **The three `assert`s** are the rule, piece by piece: BFS starts
  where it was put; it never visits a place twice (a list with repeats is
  longer than the set made from it); and the places it visits are exactly
  the reachable ones -- none missing, none extra.

Notice what the test *doesn't* say. It never says "from `a` you get
`a, b, c, d`". It doesn't need to know any answers. It only needs a rule
that's always true, and a slow way to work out the right set.

That last `assert` matters. **A do-nothing BFS that hands back just the
start place passes the first two `assert`s, and passes the "nearer
places first" property below, but fails "every place you can get to".**

PyGraphDB has seven more properties:

| Rule | Test |
|---|---|
| From any start, DFS visits every place you can get to, each once, and nowhere else | `test_dfs_visits_exactly_the_reachable_places` |
| BFS spreads like ripples: it never visits a place before one that is fewer roads away | `test_bfs_visits_nearer_places_first` |
| A shortest path follows real roads and takes the fewest; no path means unreachable | `test_shortest_path_takes_the_fewest_roads` |
| Loading a saved graph gives back the same nodes and edges, with the same types inside | `test_save_then_load_gives_back_the_same_graph` |
| Whatever bytes are in the file, loading gives a graph or a `PersistenceError`, never another error | `test_any_bytes_on_disk_load_or_raise_persistence_error` |
| Whatever JSON is in the file, loading gives a graph or a `PersistenceError`, never another error | `test_any_json_on_disk_load_or_raise_persistence_error` |
| Whatever file loads, every edge a node lists really starts or ends there, and none is counted twice | `test_a_loaded_graph_agrees_with_itself` |

## Checking Against a Model

A property checks one action on a finished town. But a graph is something
you change step by step: add a place, build a road, knock a place down,
build another road. Bugs often hide in the *order* of steps -- knocking
down a place that still has roads leading into it, say.

So the surveyor has a second trick. They carry a notebook with two lists
written by hand: every place (its label and properties), and every road
(where it starts and ends, its type and properties). After every single change to the town, they check
the town against the notebook. If the two ever disagree, something's
wrong with the town.

That notebook is a **model**: something simple that we already trust.
Here's part of the check in `tests/test_model.py`:

```python
class GraphMachine(RuleBasedStateMachine):
    """Play random adds, updates, removes and lookups on a Graph and on two dicts side by side."""

    nodes = Bundle("nodes")

    def __init__(self) -> None:
        """Make an empty graph and two empty dicts (the first nodes go in just below)."""
        super().__init__()
        self.graph = Graph()
        self.node_notes: dict[str, NodeNote] = {}
        self.edge_notes: dict[str, EdgeNote] = {}

    @rule(target=nodes, node_id=node_names(), label=labels(), properties=property_bags())
    def add_node(self, node_id: str, label: str, properties: dict[str, object]) -> str:
        """Add a node to both, or get DuplicateNodeError if the id is taken; remember the id."""
        if node_id in self.node_notes:
            with pytest.raises(DuplicateNodeError):
                self.graph.add_node(node_id, label=label, properties=properties)
        else:
            node = self.graph.add_node(node_id, label=label, properties=properties)
            assert node.node_id == node_id
            self.node_notes[node_id] = (label, dict(properties))
        return node_id

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
TestGraphModel = cast("type[unittest.TestCase]", GraphMachine.TestCase)
```

Piece by piece:

- **`RuleBasedStateMachine`** is Hypothesis's tool for testing things that
  change step by step. Hypothesis makes up a random **story** of steps and
  plays it.
- **`self.graph`, `self.node_notes` and `self.edge_notes`** are the town
  and the notebook's two lists. Every story starts with the same five places
  (`a` to `e`) and no roads, added by one `@initialize` step in the real
  file.
- **Each `@rule`** is one kind of step. It does the same thing to the
  graph and to the dicts, and checks what the graph answers: `add_node`
  must hand back the node it made, or raise `DuplicateNodeError` if the
  dict already has that id. The real file has rules to add a node or an
  edge, update one (a new label or type, and some properties merged in),
  remove a node (and every edge touching it), remove an edge, and look up
  a node or an edge. A node that isn't there must raise
  `NodeNotFoundError` from every lookup, BFS and DFS included.
- **`nodes = Bundle("nodes")`** is a bag of ids used earlier in the story.
  `add_node` puts its id in the bag (`target=nodes`), and later rules pull
  ids out, so new roads join places that really exist (or used to).
- **Each `@invariant()`** runs after every single step. This one is the
  headline rule again: from every place, BFS and DFS reach exactly what
  the notebook says. `roads()` turns the notebook into the same dict of
  sets the property uses. Two more invariants check every place's roads,
  degrees and neighbours, and the full lists of nodes and edges.
- **`TestGraphModel = ...TestCase`** turns the machine into a test that
  pytest can find and run. One run plays 100 random stories, each up to
  20 steps long (the `settings` line above it; Hypothesis's default is
  50, which finds the same bugs but takes most of the run time).

The notebook is a good model because it's obviously right and it's *not*
`Graph`'s code. `Graph` keeps a list of roads at every place so it never
has to look at the whole town; the notebook just reads every road, every
time. If we built the model by copying `Graph`, any bug would be in both,
and they'd agree perfectly about the wrong answer.

## Try It Yourself

Let's break BFS on purpose and watch the surveyor find it.

Open `src/pygraphdb/traversal.py`, find `bfs`, and change the line that
marks the starting place as visited, as if you'd forgotten it:

```python
    pass  # was: visited.add(start_id)
```

Run the property tests:

```bash
uv run pytest tests/test_properties.py tests/test_model.py --no-cov
```

Hypothesis reports this (trimmed to the interesting part):

```
road_map = RoadMap(places=[''], roads=[('', '')])

    @given(road_map=road_maps())
    def test_bfs_visits_exactly_the_reachable_places(road_map: RoadMap) -> None:
        """From any start, BFS visits every place you can get to, each once, and nowhere else."""
        graph = graph_of(road_map)
        for start in road_map.places:
            visited = [node.node_id for node in bfs(graph, start)]
            assert visited[0] == start
>           assert len(visited) == len(set(visited))
E           AssertionError: assert 2 == 1
E            +  where 2 = len(['', ''])
E            +  and   1 = len({''})
E            +    where {''} = set(['', ''])
E           Failing test case: test_bfs_visits_exactly_the_reachable_places(
E               road_map=RoadMap(places=[''], roads=[('', '')]),
E           )
```

Look at how small that is. Hypothesis tried towns with up to five places and
eight roads, then shrank the failure all the way down to **one place
called `""`, with one road that loops straight back to it**. BFS
starts at `""`, but never writes it down as visited. So when it follows
the loop, `""` looks brand new, and it visits it a second time:
`['', '']`.

The example tests all still pass. Only the property notices. None of the
BFS example towns has a road leading back to the start, so the forgotten
line never mattered.

`test_bfs_visits_exactly_the_reachable_places` catches it, and so do
`test_bfs_visits_nearer_places_first` and the model check. The DFS,
shortest path and save-file properties stay green, because the bug is
only in `bfs`.

Put the line back to `visited.add(start_id)` and run the tests again.
They pass.

!!! tip "Older Hypothesis versions"
    Older versions of Hypothesis print `Falsifying example:` instead of
    `Failing test case:`. It means the same thing.

## A Bug We Found

`test_a_loaded_graph_agrees_with_itself` loads random files shaped like
save files and checks the graph that comes back is in one piece. On the
real code, it failed. Hypothesis found the bug two ways at once, so it
printed both, each with a `|` down its left side to show which failure a
line belongs to. Here's one:

```
    |     assert all(
    |         edge.source_id == node.node_id for edge in graph.get_outgoing_edges(node.node_id)
    |     )
    | AssertionError: assert False
    | Failing test case: test_a_loaded_graph_agrees_with_itself(
    |     document={'nodes': [{}, {'node_id': 'a'}],
    |         'edges': [{}, {'source_id': 'a'}]},
    | )
```

Two nodes, `""` and `"a"` (a card with no `node_id` gets the id `""`).
Two edges with no `edge_id`, so **both get the id `""`**: the first goes
`"" -> ""`, the second `"a" -> ""`.

`Graph.from_dict` filed each edge in the list of all edges, and in its
start node's road list. The second edge replaced the first in the list
of all edges, because they share an id, but node `""`'s road list still
said "edge `""` leaves me". So node `""` listed a road that really
started at `"a"`, and removing that edge later crashed with a `KeyError`.

`add_edge` already refuses a taken id, so the example tests, which built
graphs with `add_edge` or loaded files `save_graph` wrote, could never
make two edges with one id. The surveyor's random save files do it all
the time.

The fix makes `from_dict` refuse a taken id, just like `add_edge`, and
`load_graph` turns that into a `PersistenceError`:

```python
if edge.edge_id in graph._edges:  # was: no check at all
    msg = f"Edge '{edge.edge_id}' already exists"
    raise DuplicateEdgeError(msg)
```

The shrunk file is now an ordinary example test in `tests/test_graph.py`:

```python
def test_from_dict_refuses_two_edges_with_one_id(self) -> None:
    """Two edges sharing an id raise DuplicateEdgeError, as add_edge does.

    Regression: found by a property test. The second edge used to replace
    the first in the edge list but not in its node's road list, so node
    ``""`` listed an edge that started at ``"a"``.
    """
    data: dict[str, object] = {
        "nodes": [{}, {"node_id": "a"}],
        "edges": [{}, {"source_id": "a"}],
    }
    with pytest.raises(DuplicateEdgeError):
        Graph.from_dict(data)
```

Two more loading bugs turned up the same way, pinned in
`tests/test_persistence.py`: a file holding the single byte `0x80` (not
UTF-8 text) crashed with `UnicodeDecodeError`, and
`{"nodes": [], "edges": [{}]}` (an edge to a missing node) crashed with
`NodeNotFoundError`. Both now give a `PersistenceError`.

## Run It Yourself

Run just the property tests, and the model check (100 examples each, the
same every time):

```bash
uv run pytest tests/test_properties.py tests/test_model.py --no-cov
```

The `--no-cov` turns off the coverage check, which expects the *whole*
test suite to run and would fail on two files.

Run them the long way (2,000 random examples each, different every run)
to hunt for rarer bugs. It takes about 5 minutes:

```bash
uv run pytest tests/test_properties.py tests/test_model.py --no-cov --hypothesis-profile=thorough
```

The normal run uses a fixed seed, so it tries the same inputs every time
and a passing build means the same thing on every computer. The thorough
run is random, so each time you run it the surveyor draws a brand-new
pile of towns. Both settings live in `conftest.py` at the top of the
project.

## Your Turn

Write one new property for PyGraphDB. Think about `all_paths(graph,
start, end)`. Whatever the town, what must be true of every path it
returns? Where does it start and end? Can it visit a place twice? Does
each step follow a real road? What's the strategy? What's the `assert`?
Run it and watch it pass. Then break `all_paths` on purpose and watch the
surveyor find it.
