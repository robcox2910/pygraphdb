"""Strategies -- recipes for random place names and road maps, shared by the property tests.

A strategy tells Hypothesis how to invent one kind of input. Each one here
is a named function, named for what it makes, with a one-line docstring.
``tests/test_properties.py`` and ``tests/test_model.py`` both use them.

This file also holds the *slow, obvious* answers the tests compare against:
a road map is kept as a plain dict of sets, and "where can I get to from
here?" is worked out by a loop that keeps adding places until nothing new
turns up. No queue, no stack, no visited list -- nothing borrowed from
``pygraphdb.traversal``.
"""

from dataclasses import dataclass

from hypothesis import strategies as st

# A random map has at most this many places and roads. Bigger maps find the
# same bugs (a failure shrinks to a tiny map anyway) and take longer to make.
MOST_PLACES = 5
MOST_ROADS = 8


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


def steps_from(neighbours: dict[str, set[str]], start: str) -> dict[str, int]:
    """Return how many roads it takes to reach each reachable place, the slow, obvious way."""
    # Start knowing only that ``start`` is 0 steps away. Then keep asking every
    # road "would going along you be a quicker way to your far end?" until no
    # road can make anything quicker.
    steps = {start: 0}
    changed = True
    while changed:
        changed = False
        for here in list(steps):
            for there in neighbours[here]:
                if there not in steps or steps[here] + 1 < steps[there]:
                    steps[there] = steps[here] + 1
                    changed = True
    return steps
