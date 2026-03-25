# SQL Style Guide

> **Sources:** GitLab SQL Style Guide (gitlab.com/gitlab-org/gitlab/-/blob/master/doc/development/sql.md), dbt SQL Style Guide (docs.getdbt.com/docs/guides/best-practices), Itzik Ben-Gan T-SQL best practices

---

## A. Formatting & Style

### Keywords

**All SQL keywords UPPERCASE:**

```sql
-- ✅ GOOD
SELECT
    u.id,
    u.email,
    o.total
FROM users AS u
INNER JOIN orders AS o ON o.user_id = u.id
WHERE u.is_active = TRUE
    AND o.created_at >= NOW() - INTERVAL '30 days'
ORDER BY o.created_at DESC;

-- ❌ BAD: mixed case keywords
select u.id, u.email from users u where u.is_active = true;
```

### Indentation

- **4 spaces** per indent level
- Each clause (`SELECT`, `FROM`, `WHERE`, `GROUP BY`, etc.) starts on its own line
- Comma-first style (dbt convention) OR trailing commas — choose one per project and stick to it:

```sql
-- ✅ Trailing comma style (GitLab convention)
SELECT
    user_id,
    email,
    created_at,
    is_active
FROM users

-- ✅ Leading comma style (dbt convention — preferred for long column lists)
SELECT
      user_id
    , email
    , created_at
    , is_active
FROM users
```

### Aliases

Always use the `AS` keyword for aliases (GitLab SQL Style):

```sql
-- ✅ GOOD
SELECT
    u.id AS user_id,
    u.email AS user_email
FROM users AS u

-- ❌ BAD: omitting AS
SELECT u.id user_id FROM users u
```

---

## B. Naming Conventions (dbt Style Guide)

| Object | Convention | Example |
|--------|-----------|---------|
| Tables | `snake_case`, plural | `users`, `order_items`, `payment_transactions` |
| Columns | `snake_case` | `user_id`, `total_price`, `created_at` |
| Primary key | `id` (simple) or `<table_singular>_id` | `id` or `user_id` |
| Foreign keys | `<referenced_table_singular>_id` | `user_id`, `order_id` |
| Boolean columns | `is_`, `has_`, `can_` prefix | `is_active`, `has_subscription`, `is_deleted` |
| Timestamps | `created_at`, `updated_at`, `deleted_at` | Standard names — always `_at` suffix |
| Indexes | `idx_<table>_<columns>` | `idx_orders_user_id`, `idx_users_email` |
| Unique constraints | `uq_<table>_<columns>` | `uq_users_email` |
| Foreign key constraints | `fk_<table>_<referenced_table>` | `fk_orders_users` |
| Check constraints | `chk_<table>_<description>` | `chk_orders_positive_total` |

---

## C. Query Patterns

### Avoid SELECT *

```sql
-- ❌ BAD: SELECT * — fragile, exposes all columns, can't use covering indexes
SELECT * FROM orders WHERE user_id = $1;

-- ✅ GOOD: explicit column list
SELECT
    id,
    user_id,
    total,
    status,
    created_at
FROM orders
WHERE user_id = $1;
```

### Join Style

Use `INNER JOIN` and `LEFT JOIN` — avoid `RIGHT JOIN` (reorganize query to use LEFT JOIN instead for consistency):

```sql
-- ✅ GOOD: explicit INNER JOIN
SELECT
    u.id AS user_id,
    u.email,
    COUNT(o.id) AS order_count
FROM users AS u
INNER JOIN orders AS o ON o.user_id = u.id
WHERE u.is_active = TRUE
GROUP BY u.id, u.email;

-- ❌ BAD: implicit join (comma in FROM) — hard to read, error-prone
SELECT u.id, o.total
FROM users u, orders o
WHERE u.id = o.user_id;
```

### CTEs (Common Table Expressions) Over Subqueries

```sql
-- ✅ GOOD: CTEs are readable and can be referenced multiple times
WITH active_users AS (
    SELECT id, email
    FROM users
    WHERE is_active = TRUE
        AND created_at >= '2024-01-01'
),
user_totals AS (
    SELECT
        u.id,
        u.email,
        COALESCE(SUM(o.total), 0) AS lifetime_total
    FROM active_users AS u
    LEFT JOIN orders AS o ON o.user_id = u.id
    GROUP BY u.id, u.email
)
SELECT *
FROM user_totals
WHERE lifetime_total > 1000
ORDER BY lifetime_total DESC;

-- ❌ BAD: nested subqueries — hard to read
SELECT *
FROM (
    SELECT u.id, u.email, COALESCE(SUM(o.total), 0) AS lifetime_total
    FROM (SELECT id, email FROM users WHERE is_active = TRUE) u
    LEFT JOIN orders o ON o.user_id = u.id
    GROUP BY u.id, u.email
) t
WHERE t.lifetime_total > 1000;
```

### NULL Handling

```sql
-- ✅ GOOD: use COALESCE for NULL defaults
SELECT COALESCE(discount_amount, 0) AS discount_amount FROM orders;

-- ✅ GOOD: use IS NULL / IS NOT NULL (never = NULL)
SELECT * FROM users WHERE deleted_at IS NULL;  -- active users

-- ❌ BAD: = NULL always evaluates to NULL (never TRUE)
SELECT * FROM users WHERE deleted_at = NULL;   -- returns no rows
```

---

## D. Comments

```sql
-- ✅ GOOD: comment explaining non-obvious business logic
-- Include users who signed up before migration (pre-2024) even if email not verified
SELECT id, email
FROM users
WHERE is_active = TRUE
    OR (created_at < '2024-01-01' AND email_verified = FALSE);

-- ✅ TODO format
-- TODO(alice@example.com, 2025-03-15, INFRA-423): Replace with materialized view
-- after PostgreSQL 15 upgrade (supports incremental refresh)
SELECT user_id, SUM(total) AS lifetime_value FROM orders GROUP BY user_id;
```

---

## E. Performance

### Always Parameterize (Security + Plan Caching)

```sql
-- ❌ BAD: literal value — different plan per query, SQLi risk
SELECT * FROM users WHERE email = 'alice@example.com';

-- ✅ GOOD: parameterized — plan cached, SQLi impossible
SELECT * FROM users WHERE email = $1;  -- PostgreSQL
SELECT * FROM users WHERE email = ?;   -- MySQL / SQLite
SELECT * FROM users WHERE email = :email;  -- Oracle / SQLAlchemy
```

### Index Rules

- Index every column used in `WHERE`, `JOIN ON`, or `ORDER BY`
- Add composite indexes for multi-column WHERE clauses (column order matters: most selective first)
- UNIQUE constraint creates an index automatically
- `EXPLAIN ANALYZE` every query on tables > 100k rows before releasing

---

## F. Security

```sql
-- ❌ NEVER: dynamic SQL with user input
EXECUTE 'SELECT * FROM ' || table_name || ' WHERE id = ' || user_id;

-- ✅ GOOD: parameterized, whitelisted table names
-- Whitelist allowed tables at application level before using in SQL
EXECUTE 'SELECT * FROM orders WHERE id = $1' USING order_id;
```
