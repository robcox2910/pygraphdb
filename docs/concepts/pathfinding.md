# Pathfinding -- GPS Directions

## The Analogy

When you type an address into Google Maps, it finds the **shortest route** from where you are to where you want to go. Our pathfinding algorithm does the same thing for graphs!

Instead of streets and intersections, we have nodes and edges. Instead of distance in kilometers, we count the number of edges (hops) between nodes.

## How It Works

We use BFS (breadth-first search) to find the shortest path. Why? Because BFS explores nodes layer by layer:
- First, all nodes 1 hop away
- Then, all nodes 2 hops away
- Then 3 hops, and so on...

The first time BFS reaches your destination, it **guarantees** that's the shortest path!

## Code Example

```python
from pygraphdb import Graph, shortest_path

g = Graph()
for city in ["London", "Paris", "Berlin", "Rome", "Madrid"]:
    g.add_node(city, label="City")

g.add_edge("e1", "London", "Paris", rel_type="TRAIN")
g.add_edge("e2", "Paris", "Berlin", rel_type="TRAIN")
g.add_edge("e3", "Berlin", "Rome", rel_type="TRAIN")
g.add_edge("e4", "London", "Madrid", rel_type="FLIGHT")
g.add_edge("e5", "Madrid", "Rome", rel_type="FLIGHT")

# Shortest path from London to Rome
path = shortest_path(g, "London", "Rome")
# Result: London -> Madrid -> Rome (2 hops, not 3 via Paris-Berlin)
```

## Finding ALL Paths

Sometimes you don't just want the shortest route -- you want to see all options! The `all_paths` function finds every possible path:

```python
from pygraphdb import all_paths

paths = all_paths(g, "London", "Rome")
# Two paths: London->Paris->Berlin->Rome and London->Madrid->Rome
```
