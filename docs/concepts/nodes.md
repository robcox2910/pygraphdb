# Nodes -- People at a Party

## The Analogy

Imagine you're at a big party. Every person there is a **node**. Each person has:
- A **wristband number** (their unique ID -- no two people share one)
- A **group name tag** that says what kind of person they are: "Student", "Teacher", "Parent"
- A **fact sheet** with details about them: their name, age, favorite food, etc.

In our graph database, a Node works exactly the same way:

```python
from pygraphdb import Node

# Create a person at the party
alice = Node(
    node_id="alice-01",      # Wristband number
    label="Student",          # Group name tag
    properties={              # Fact sheet
        "name": "Alice",
        "age": 13,
        "favorite_food": "pizza"
    }
)
```

## Why Nodes Need Unique IDs

If two people at the party both had wristband #42, how would you tell them apart when someone says "bring me person #42"? You couldn't! That's why every node needs a unique ID.

## Labels are Like Categories

Labels help you organize nodes into groups. At a school, you might have:
- `Student` nodes
- `Teacher` nodes
- `Classroom` nodes

This makes it easy to ask questions like "show me all the Students."

## Properties are Flexible

Unlike a rigid spreadsheet where every row must have the same columns, node properties are flexible. One Student might have a `gpa` property while another doesn't -- and that's perfectly fine!
