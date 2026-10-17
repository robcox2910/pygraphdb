# Edges -- Friendships and Handshakes

## The Analogy

At our party, people don't just stand around alone -- they interact! When Alice shakes hands with Bob, that handshake is an **edge**. It connects two people and describes their relationship.

An edge has:
- A **direction**: Alice shook Bob's hand (Alice -> Bob). This is a *directed* edge, like a one-way street.
- A **type**: What kind of relationship? "FRIENDS_WITH", "CLASSMATES", "SIBLINGS"
- **Properties**: Extra details -- "became friends in 2023", "best friends" vs "acquaintances"

```python
from pygraphdb import Graph

g = Graph()
g.add_node("alice", label="Student", properties={"name": "Alice"})
g.add_node("bob", label="Student", properties={"name": "Bob"})

# The handshake!
g.add_edge("e1", "alice", "bob", rel_type="FRIENDS_WITH", properties={"since": 2023})
```

## Direction Matters

Our edges are **directed** -- like arrows, not lines. "Alice FOLLOWS Bob" doesn't mean "Bob FOLLOWS Alice." If you want a mutual friendship, you need two edges:

```python
g.add_edge("e1", "alice", "bob", rel_type="FRIENDS_WITH")
g.add_edge("e2", "bob", "alice", rel_type="FRIENDS_WITH")
```

## Multiple Relationships

Two nodes can have multiple edges between them! Alice might KNOW Bob (they've met) AND WORK_WITH Bob (they're lab partners). Each relationship is a separate edge with its own type and properties.

## Every Node Keeps Its Own Address Book

How do you find someone's friends? The slow way is to read *every*
friendship in the whole school and pick out the ones that mention them.
That gets slower and slower as the school grows.

PyGraphDB does it the fast way: every node keeps its own little **address
book** -- one list of the edges going out from it and one list of the edges
coming in. Asking "who are Alice's friends?" just opens Alice's address book.
It doesn't matter if the school has ten friendships or ten million; it's
just as quick.

Real graph databases (like Neo4j) call this **index-free adjacency**, and
it's the whole reason they're good at following connections. Every time an
edge is added or removed, both end nodes' address books are updated, so they
never get out of step. Neighbours come back in the order their edges were
added, so you get the same answer every time.
