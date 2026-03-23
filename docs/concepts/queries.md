# Queries -- Asking Questions About Your Network

## The Analogy

Imagine you could talk to your whiteboard and ask it questions in English:
- "Show me all the Students"
- "Who does Alice know?"
- "Find everyone Alice knows through Bob"

Real graph databases use a language called **Cypher** for exactly this. It's like SQL (the language for regular databases) but designed for graphs. Our version is simplified but follows the same ideas!

## The Query Language

Our queries follow this pattern:

```
MATCH (variable:Label)-[:RELATIONSHIP]->(other_variable) WHERE conditions RETURN result
```

Let's break that down:
- `MATCH` = "Find me..."
- `(n:Person)` = "...a node labeled Person (call it n)..."
- `-[:KNOWS]->` = "...connected by a KNOWS relationship to..."
- `(m)` = "...another node (call it m)..."
- `WHERE n.name = "Alice"` = "...but only where n's name is Alice..."
- `RETURN m` = "...and give me back m"

## Code Examples

```python
from pygraphdb import Graph, execute_query

g = Graph()
g.add_node("1", label="Person", properties={"name": "Alice"})
g.add_node("2", label="Person", properties={"name": "Bob"})
g.add_node("3", label="Person", properties={"name": "Charlie"})
g.add_edge("e1", "1", "2", rel_type="KNOWS")
g.add_edge("e2", "1", "3", rel_type="KNOWS")

# Find all people
everyone = execute_query(g, "MATCH (n:Person) RETURN n")

# Find Alice specifically
alice = execute_query(g, 'MATCH (n:Person) WHERE n.name = "Alice" RETURN n')

# Find everyone Alice knows
alice_friends = execute_query(g, 'MATCH (n:Person)-[:KNOWS]->(m) WHERE n.name = "Alice" RETURN m')
```

## Query Parts Cheat Sheet

| Part | Meaning | Example |
|------|---------|---------|
| `MATCH` | Start searching | `MATCH (n:Person)` |
| `(n:Label)` | A node with a label | `(p:Student)` |
| `-[:TYPE]->` | A directed relationship | `-[:KNOWS]->` |
| `WHERE` | Filter condition | `WHERE n.age = "13"` |
| `RETURN` | What to give back | `RETURN n` |
