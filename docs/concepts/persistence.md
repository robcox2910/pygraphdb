# Persistence -- Saving Your Graph

## The Analogy

Think about saving a video game. You've spent hours building your world, and you don't want to lose it when you turn off the computer. You hit "Save" and all your progress is written to a file. Next time, you hit "Load" and everything is exactly as you left it.

Our graph database works the same way! You can save your entire graph (every node and every edge) to a **JSON file** on disk, and load it back later.

## What is JSON?

JSON (JavaScript Object Notation) is a text format that's easy for both humans and computers to read:

```json
{
  "nodes": [
    {"node_id": "1", "label": "Person", "properties": {"name": "Alice"}},
    {"node_id": "2", "label": "Person", "properties": {"name": "Bob"}}
  ],
  "edges": [
    {"edge_id": "e1", "source_id": "1", "target_id": "2", "rel_type": "KNOWS", "properties": {}}
  ]
}
```

## Code Example

```python
from pygraphdb import Graph, save_graph, load_graph

# Build your graph
g = Graph()
g.add_node("alice", label="Person", properties={"name": "Alice"})
g.add_node("bob", label="Person", properties={"name": "Bob"})
g.add_edge("e1", "alice", "bob", rel_type="FRIENDS_WITH")

# Save it (like saving a game)
save_graph(g, "my_friends.json")

# Later... load it back (like loading a saved game)
g2 = load_graph("my_friends.json")
print(g2.get_node("alice").properties["name"])  # "Alice"
```

## In-Memory Serialization

Sometimes you want a JSON string without saving to disk (for example, to send over a network):

```python
from pygraphdb import graph_to_json, graph_from_json

json_string = graph_to_json(g)
restored = graph_from_json(json_string)
```
