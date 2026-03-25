# SQL Query Optimization

---

## EXPLAIN ANALYZE (PostgreSQL)

```sql
-- Always EXPLAIN ANALYZE before releasing queries on large tables
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.id, u.email, COUNT(o.id) AS order_count
FROM users AS u
INNER JOIN orders AS o ON o.user_id = u.id
WHERE u.is_active = TRUE
GROUP BY u.id, u.email;
```

**What to look for:**
- `Seq Scan` on large tables — usually indicates a missing index
- `Hash Join` vs `Index Scan` — Hash Join is fine for large joins; Index Scan preferred for selective queries
- `Rows=` estimate vs `actual rows` — large discrepancy means stale statistics (`ANALYZE`)
- `Buffers: shared hit=` vs `shared read=` — high `read` means data not in cache

---

## Index Strategy

### B-tree Index (default — most common)

```sql
-- Single column
CREATE INDEX idx_orders_user_id ON orders (user_id);

-- Composite — order matters: equality first, then range
CREATE INDEX idx_orders_user_status ON orders (user_id, status, created_at DESC);
-- This covers: WHERE user_id = $1 AND status = $2 ORDER BY created_at DESC

-- Partial index — index only a subset of rows (smaller, faster)
CREATE INDEX idx_orders_pending ON orders (user_id, created_at)
    WHERE status = 'pending';
```

### Index for LIKE queries (PostgreSQL)

```sql
-- For LIKE 'prefix%' queries, use a standard B-tree index
CREATE INDEX idx_users_email ON users (email);
-- LIKE 'alice%' can use this

-- For arbitrary LIKE '%substring%', use GIN with pg_trgm
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_products_name_trgm ON products USING GIN (name gin_trgm_ops);
```

---

## N+1 Query Pattern (Application Side)

```sql
-- ❌ BAD (from application): N+1 queries
-- for user_id in users:
--   SELECT * FROM orders WHERE user_id = $1  ← executes N times

-- ✅ GOOD: single JOIN query
SELECT
    u.id AS user_id,
    u.email,
    o.id AS order_id,
    o.total,
    o.status
FROM users AS u
LEFT JOIN orders AS o ON o.user_id = u.id
WHERE u.id = ANY($1);  -- pass array of user IDs
```

---

## Pagination

```sql
-- ❌ BAD: OFFSET pagination — slow for large offsets (scans all previous rows)
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 10000;

-- ✅ GOOD: keyset / cursor pagination — O(log n) regardless of page
SELECT *
FROM orders
WHERE created_at < $1  -- cursor: last seen created_at
    AND id < $2        -- tiebreaker: last seen id
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

---

## Vacuuming (PostgreSQL)

- PostgreSQL relies on VACUUM to reclaim dead rows from UPDATEs and DELETEs
- Enable `autovacuum` (default in PostgreSQL) — never disable it
- For high-UPDATE tables (like order status), monitor bloat with:

```sql
SELECT schemaname, tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    n_dead_tup, n_live_tup,
    round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 2) AS dead_pct
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```
