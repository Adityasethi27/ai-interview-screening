# Databases and Persistence

## Relational model and normalization
Relational databases store data in tables with defined relationships. **Normalization**
organizes columns to reduce redundancy and update anomalies:
- **1NF**: atomic values, no repeating groups.
- **2NF**: no partial dependency on part of a composite key.
- **3NF**: no transitive dependency between non-key columns.
Normalization keeps writes consistent; **denormalization** deliberately duplicates
data to speed reads, trading storage and write complexity for query performance. The
right point on that spectrum depends on read/write ratios.

## Indexing
An index is an auxiliary data structure (usually a **B-tree**) that lets the
database find rows without scanning the whole table, turning O(n) scans into
O(log n) lookups. Trade-offs:
- Indexes speed up reads and `WHERE`/`JOIN`/`ORDER BY` on indexed columns.
- They slow down writes (every insert/update maintains the index) and consume
  storage.
- **Composite indexes** cover multi-column queries but only help when the query
  uses a **leftmost prefix** of the index columns.
- **Covering indexes** include all columns a query needs, avoiding a table lookup.
Hash indexes are great for equality but not range queries; B-trees support both
equality and ranges. Use `EXPLAIN`/query plans to verify an index is actually used.

## Transactions and ACID
A transaction groups operations so they succeed or fail as a unit. **ACID**:
- **Atomicity**: all-or-nothing.
- **Consistency**: transactions move the DB between valid states, preserving
  constraints.
- **Isolation**: concurrent transactions do not corrupt each other.
- **Durability**: once committed, data survives crashes (write-ahead logging).

## Isolation levels and anomalies
Weaker isolation allows anomalies but improves concurrency:
- **Read Uncommitted**: dirty reads possible.
- **Read Committed**: no dirty reads; non-repeatable reads possible.
- **Repeatable Read**: stable reads within a transaction; phantom rows possible.
- **Serializable**: behaves as if transactions ran one at a time; strongest, most
  contention.
Choose the weakest level that preserves correctness for your workload.

## Optimistic vs pessimistic concurrency
- **Pessimistic locking** locks rows before modifying, blocking others; good under
  high contention but risks deadlocks.
- **Optimistic concurrency** assumes conflicts are rare: read a version number,
  and on write check it hasn't changed (compare-and-set). Cheaper when contention
  is low.

## SQL vs NoSQL
- **Relational (SQL)** databases give strong consistency, joins, and a rigid schema
  — ideal for transactional systems with complex relationships.
- **Document stores** (e.g. MongoDB) offer flexible schemas and easy horizontal
  sharding for hierarchical data.
- **Key-value stores** (e.g. Redis) give microsecond lookups for caching/sessions.
- **Wide-column and graph** stores target analytics and highly connected data.
Choose by access patterns, consistency needs, and scale — not familiarity.

## The CAP theorem
In a distributed store, during a network **partition** you can guarantee either
**consistency** (every read sees the latest write) or **availability** (every
request gets a response), not both. Systems pick a stance: CP systems refuse some
requests to stay consistent; AP systems stay available and reconcile later
(eventual consistency).

## N+1 queries and connection pooling
The **N+1 problem** issues one query per item in a loop instead of a single joined
/batched query — a common performance killer; fix with joins, `IN` batching, or
eager loading. A **connection pool** reuses a bounded set of DB connections across
requests, since opening connections is expensive and databases cap concurrent
connections.
