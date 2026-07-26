"""Custom exceptions for PyGraphDB.

Think of these like warning signs at a playground -- they tell you when
something went wrong so you can fix it instead of getting confused by
a mysterious crash.

Each exception type describes a specific kind of problem:
- A node you asked for doesn't exist
- An edge you asked for doesn't exist
- You tried to add something that's already there
- A query you wrote has a mistake in it
"""


class GraphError(Exception):
    """Base exception for all graph database errors."""


class NodeNotFoundError(GraphError):
    """Raise when a requested node does not exist in the graph.

    Like looking for a person at a party who never showed up.
    """


class EdgeNotFoundError(GraphError):
    """Raise when a requested edge does not exist in the graph.

    Like looking for a friendship between two people who don't know each other.
    """


class DuplicateNodeError(GraphError):
    """Raise when trying to add a node with an ID that already exists.

    Like trying to give two different people the exact same name tag at a party.
    """


class DuplicateEdgeError(GraphError):
    """Raise when trying to add an edge whose id is already taken.

    Like giving two different roads the exact same street sign -- an edge
    with this id already exists. (Two separate roads between the same pair
    of buildings are fine, as long as each has its own sign.)
    """


class QuerySyntaxError(GraphError):
    """Raise when a query string has invalid syntax.

    Like writing a sentence with the words in the wrong order --
    the computer can't understand what you're asking.
    """
