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

## Saving Safely

The simple way to save -- wipe the file, then write it out again -- has a
nasty problem: if the computer crashes halfway through, you're left with half
a file, and your data is gone.

So saving works like a careful student copying out their homework:

1. Write the new version on a **fresh sheet** -- a temporary file right next
   to the real one.
2. Make sure the **ink is dry** -- `fsync` pushes the bytes out of the
   computer's memory and onto the disk.
3. **Swap** the fresh sheet in for the old one in a single instant step.

At every moment there's a complete file: the old one or the new one, never
half of each. Real databases like SQLite and PostgreSQL use the same trick.
The code lives in `atomic.py`.

## When a Save File Is Damaged

Loading is careful too. If the file is missing, isn't valid JSON, or isn't
one of our save files at all, `load_graph` raises a `PersistenceError`
that names the file. It never quietly hands back an empty database -- that
would be like a game starting a brand-new save and then overwriting your
old one the next time you pressed "save".
