# Traversal -- Exploring a Maze

## The Analogy

Imagine you're dropped into a maze. You need to visit every room. There are two main strategies:

### BFS: The Ripple Strategy

Drop a stone in a pond and watch the ripples spread outward in circles. **Breadth-First Search (BFS)** works the same way:

1. Visit your starting room
2. Visit ALL rooms one step away
3. Visit ALL rooms two steps away
4. Keep going until you've been everywhere

BFS is great when you want to find the **closest** things first -- like finding your nearest friend at the party.

### DFS: The Tunnel Strategy

Pick a tunnel and follow it as deep as you can. When you hit a dead end, backtrack and try the next tunnel. **Depth-First Search (DFS)** dives deep before going wide.

DFS is great when you want to fully explore one path before trying another -- like reading one book series completely before starting the next.

## Code Example

```python
from pygraphdb import Graph, bfs, dfs

g = Graph()
for name in ["Alice", "Bob", "Charlie", "Diana"]:
    g.add_node(name, label="Person")
g.add_edge("e1", "Alice", "Bob", rel_type="KNOWS")
g.add_edge("e2", "Alice", "Charlie", rel_type="KNOWS")
g.add_edge("e3", "Bob", "Diana", rel_type="KNOWS")

# BFS: Alice -> Bob, Charlie -> Diana
bfs_order = [n.node_id for n in bfs(g, "Alice")]

# DFS: Alice -> Bob -> Diana -> Charlie
dfs_order = [n.node_id for n in dfs(g, "Alice")]
```

## When to Use Which?

| Strategy | Best For | Think Of It As |
|----------|----------|----------------|
| BFS | Finding nearest neighbors, shortest paths | Ripples in a pond |
| DFS | Exploring all possibilities, detecting cycles | Following a trail |
