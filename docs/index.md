---
title: "Build your own graph database in Python"
---

# PyGraphDB: Build your own graph database in Python

## The Social Network Analogy

Imagine your friend group at school. You could draw everyone's name on a whiteboard and then draw lines between people who are friends. Congratulations -- you just made a graph!

A **graph database** stores data exactly like that whiteboard:
- **Nodes** are the dots (people, places, things)
- **Edges** are the lines connecting them (friendships, roads, relationships)

## Why Not Just Use a List?

You *could* keep a list of friends:
```
Alice's friends: Bob, Charlie
Bob's friends: Alice, Diana
```

But what if you want to know: "Who are Alice's friends' friends?" With a list, you'd have to jump around and search. With a graph, you just follow the lines!

## Real-World Graph Databases

Companies like Facebook, Twitter, and Google use graph databases every day:
- **Facebook**: "People You May Know" follows friend-of-friend connections
- **Google Maps**: Finds the shortest route between two places
- **Netflix**: "Because you watched X" follows similarity connections

## What You'll Learn

In this project, you'll build your own graph database from scratch:
1. How to store nodes and edges
2. How to traverse (walk through) a graph
3. How to find the shortest path between two points
4. How to search for patterns in your data
5. How to save and load your graph
6. How to write queries (questions) in a language similar to Neo4j's Cypher

Let's get started!

## Install

```bash
pip install fromscratch-pygraphdb
```

Or get the whole series at once with `pip install fromscratch-pystack`. To read the code or run the tests, clone it from [GitHub](https://github.com/robcox2910/pygraphdb).
