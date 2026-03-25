# SQL Schema Design

---

## Standard Column Conventions

Every table should have:

```sql
CREATE TABLE orders (
    id          UUID        NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    status      TEXT        NOT NULL DEFAULT 'pending'
                              CHECK (status IN ('pending', 'paid', 'cancelled', 'refunded')),
    total       NUMERIC(12, 2) NOT NULL CHECK (total >= 0),
    currency    CHAR(3)     NOT NULL CHECK (char_length(currency) = 3),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

## Normalization Rules

- **3NF minimum** for transactional tables (OLTP)
- Denormalize intentionally for read-heavy analytics (OLAP), document the trade-off
- Store money as `NUMERIC(12, 2)` or integer cents — never `FLOAT` or `DOUBLE`
- Store timestamps as `TIMESTAMPTZ` (with timezone) — never `TIMESTAMP` (naive)
- Use `UUID` for primary keys — prevents ID enumeration attacks, safe for distributed systems

## Soft Delete Pattern

```sql
-- Add deleted_at column (NULL = active, non-NULL = deleted)
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMPTZ;

-- Partial index for active records only
CREATE INDEX idx_users_active ON users (email)
    WHERE deleted_at IS NULL;

-- View for active records
CREATE VIEW active_users AS
    SELECT * FROM users WHERE deleted_at IS NULL;
```

## Foreign Key Rules

```sql
-- Always specify ON DELETE behavior explicitly:

-- Restrict deletion when referenced rows exist (safest default)
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT

-- Cascade deletion (use only when children have no independent meaning)
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE

-- Set null when parent deleted (child still exists, now orphaned)
FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
```
