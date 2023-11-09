# 📸 Query Snapshots

Queries are lazy and can only be used once (they are exhausted after being iterated).
While this provides a significant performance boost, it can be inconvenient in some cases.

This is where snapshots come in.

Snapshots provide a way to create a "checkpoint" for a Query.
The snapshot is a Query object, which can be used multiple times, without being exhausted.

Snapshots are Query objects, so they support the same behavior as regular queries.
The only difference is that they can be re-used (at the point of the snapping).

Snapshots are created using the `snap` method.

## `snap()`
::: fliq.query.Query.snap