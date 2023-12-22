# 📸 Query Representation

One of the pain points of working with lazy iterator (e.g., generators) is that they are not "inspectable".
That is, you can't see what's inside it, without consuming it. 
This makes it hard to debug, and hard to understand what's going on, which eventually slows down development.

Fliq solves this problem by providing a `repr` method for queries, 
which returns a string representation of the query, 
including peeking (see [peeking](peeking.md)) into the query without consuming it.

## `repr()`
::: fliq.query.Query.__repr__