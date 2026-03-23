# Pattern Matching -- Finding Friends Who Like Pizza

## The Analogy

Imagine you're at a huge party with 200 people. You want to find everyone who:
- Is a Student (not a Teacher or Parent)
- Likes pizza
- Is over 12 years old

You could walk up to every single person and ask... or you could use **pattern matching** to filter everyone instantly!

## How It Works

Pattern matching lets you search through your graph for nodes or edges that match specific criteria:

```python
from pygraphdb import Graph, find_nodes, find_edges

g = Graph()
g.add_node("1", label="Person", properties={"name": "Alice", "age": 13, "likes": "pizza"})
g.add_node("2", label="Person", properties={"name": "Bob", "age": 14, "likes": "tacos"})
g.add_node("3", label="Person", properties={"name": "Charlie", "age": 13, "likes": "pizza"})

# Find all pizza lovers
pizza_fans = find_nodes(g, properties={"likes": "pizza"})
# Result: Alice and Charlie

# Find all people (by label)
people = find_nodes(g, label="Person")
# Result: Alice, Bob, and Charlie
```

## Matching Edges Too

You can also search for specific relationships:

```python
# Find all FRIENDS_WITH relationships
friendships = find_edges(g, rel_type="FRIENDS_WITH")

# Find all edges from Alice
alice_connections = find_edges(g, source_id="1")
```

## Combining Criteria

The real power comes from combining label AND property filters:

```python
# Find 13-year-old people who like pizza
young_pizza_fans = find_nodes(g, label="Person", properties={"age": 13, "likes": "pizza"})
```
