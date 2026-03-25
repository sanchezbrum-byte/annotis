-- ✅ GOOD: Demonstrates SQL style conventions from sql/style-guide.md

-- ---------------------------------------------------------------------------
-- Schema: orders service
-- Uses snake_case names, explicit NOT NULL / DEFAULT, no SELECT *
-- ---------------------------------------------------------------------------

CREATE TABLE orders (
    id          UUID          NOT NULL DEFAULT gen_random_uuid(),
    user_id     UUID          NOT NULL,
    total_cents INTEGER       NOT NULL CHECK (total_cents >= 0),
    currency    CHAR(3)       NOT NULL DEFAULT 'USD',
    status      order_status  NOT NULL DEFAULT 'pending',
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ   NOT NULL DEFAULT now(),

    CONSTRAINT orders_pk PRIMARY KEY (id),
    CONSTRAINT orders_user_fk FOREIGN KEY (user_id) REFERENCES users (id)
);

-- ✅ Index supports the most common lookup pattern (status filter for workers)
CREATE INDEX idx_orders_user_id_status
    ON orders (user_id, status)
    WHERE status = 'pending';        -- partial index keeps it small

-- ---------------------------------------------------------------------------
-- Good query patterns
-- ---------------------------------------------------------------------------

-- ✅ Explicit column list — no SELECT *
-- ✅ Uppercase keywords, lowercase identifiers
-- ✅ JOIN condition on same line as JOIN keyword
-- ✅ WHERE clause predicates each on their own line, aligned
SELECT
    o.id,
    o.total_cents,
    o.currency,
    o.status,
    u.email        AS user_email,
    o.created_at
FROM orders        AS o
JOIN users         AS u ON u.id = o.user_id
WHERE o.status     = 'pending'
  AND o.created_at >= now() - INTERVAL '7 days'
ORDER BY o.created_at DESC
LIMIT 100;

-- ✅ Parameterised query placeholder (shown as $1/$2 for PostgreSQL)
-- Application code must NEVER interpolate user input into SQL strings.
SELECT id, total_cents, status
FROM   orders
WHERE  id      = $1      -- order_id parameter
  AND  user_id = $2;     -- user_id from authenticated session

-- ✅ CTE breaks down a complex query into readable steps
WITH recent_paid AS (
    SELECT
        user_id,
        SUM(total_cents) AS total_spent_cents,
        COUNT(*)         AS order_count
    FROM  orders
    WHERE status     = 'paid'
      AND created_at >= date_trunc('month', now())
    GROUP BY user_id
)
SELECT
    u.id,
    u.email,
    rp.total_spent_cents,
    rp.order_count
FROM  users        AS u
JOIN  recent_paid  AS rp ON rp.user_id = u.id
ORDER BY rp.total_spent_cents DESC
LIMIT 20;

-- ✅ UPSERT using ON CONFLICT — atomic, no lost updates
INSERT INTO order_summaries (user_id, total_cents, updated_at)
VALUES ($1, $2, now())
ON CONFLICT (user_id)
DO UPDATE SET
    total_cents = order_summaries.total_cents + EXCLUDED.total_cents,
    updated_at  = EXCLUDED.updated_at;
