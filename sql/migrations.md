# SQL Migrations

---

## Principles for Safe Migrations

1. **Migrations must be backward compatible** — old application code must work with the new schema
2. **Expand-contract pattern** for breaking changes — never drop a column in the same release that stops using it
3. **Never modify existing migration files** — add new ones
4. **Migrations run in CI** — merge blocks if migration fails
5. **Test rollbacks** — every migration should have a tested `down` migration

---

## Expand-Contract Pattern

Rename a column safely across multiple deployments:

```
Release 1 (expand):
  - Add new column: ALTER TABLE orders ADD COLUMN customer_email TEXT;
  - Application writes to both old (email) and new (customer_email) columns

Release 2 (migrate):
  - Backfill: UPDATE orders SET customer_email = email WHERE customer_email IS NULL;
  - Application reads from new column, writes to both

Release 3 (contract):
  - Application only reads/writes new column
  - Drop old column: ALTER TABLE orders DROP COLUMN email;
```

---

## Safe Operations

**Always safe (no lock, no downtime):**
```sql
-- Add nullable column
ALTER TABLE orders ADD COLUMN notes TEXT;

-- Add column with DEFAULT (PostgreSQL 11+)
ALTER TABLE orders ADD COLUMN currency TEXT NOT NULL DEFAULT 'USD';

-- Add index CONCURRENTLY (non-blocking)
CREATE INDEX CONCURRENTLY idx_orders_status ON orders (status);

-- Rename column (application must be updated concurrently)
-- Use expand-contract instead of direct rename
```

**Requires caution (may lock):**
```sql
-- Adding NOT NULL to existing column (backfill first!)
-- ❌ BAD: will fail if any NULL exists
ALTER TABLE orders ALTER COLUMN email SET NOT NULL;

-- ✅ GOOD: add with default first
ALTER TABLE orders ALTER COLUMN email SET DEFAULT '';
UPDATE orders SET email = '' WHERE email IS NULL;
ALTER TABLE orders ALTER COLUMN email SET NOT NULL;
ALTER TABLE orders ALTER COLUMN email DROP DEFAULT;
```

**Dangerous (table lock, avoid in production):**
```sql
-- Changing column type
ALTER TABLE orders ALTER COLUMN total TYPE NUMERIC(14,2);
-- Use: add new column, backfill, swap at application level, drop old column
```

---

## Migration File Naming

```
V1__create_users_table.sql
V2__create_orders_table.sql
V3__add_currency_to_orders.sql
V4__add_index_orders_user_id.sql
V5__add_deleted_at_to_users.sql
```

- Sequential versioned numbers (Flyway) or timestamps (`20250315120000_add_currency.sql`)
- Descriptive names explaining what the migration does
- Never include the word "migration" — it's redundant
