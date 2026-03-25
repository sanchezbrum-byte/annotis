-- ❌ BAD: This file demonstrates common SQL anti-patterns. Do NOT use as a template.

-- ❌ BAD: mixed case keywords and identifiers — inconsistent style
create Table Orders (
    Id int,                      -- ❌ BAD: no UUID, no DEFAULT, no NOT NULL
    UserId int,                  -- ❌ BAD: PascalCase identifier
    total FLOAT,                 -- ❌ BAD: FLOAT for money — floating-point rounding errors
    Status VARCHAR(50),          -- ❌ BAD: magic strings instead of enum/check constraint
    ts TIMESTAMP                 -- ❌ BAD: abbreviated, no DEFAULT, no timezone
    -- ❌ BAD: no PRIMARY KEY declared
);

-- ❌ BAD: SELECT * — brittle, sends unnecessary data over the wire
SELECT * FROM orders;

-- ❌ BAD: implicit JOIN (comma syntax) — hard to see join conditions
SELECT *
FROM orders, users
WHERE orders.UserId = users.Id;  -- ❌ BAD: no table alias, mixed case

-- ❌ BAD: string concatenation — SQL injection if $user_input is from user
-- (Shown here as pseudocode to illustrate the anti-pattern)
-- query = "SELECT * FROM orders WHERE id = '" + user_input + "'"

-- ❌ BAD: function call on indexed column defeats the index
SELECT * FROM orders
WHERE YEAR(created_at) = 2024;   -- ❌ BAD: use range instead: created_at BETWEEN ...

-- ❌ BAD: N+1 query pattern (pseudocode illustrating the pattern to avoid)
-- for each order in orders:
--     SELECT * FROM users WHERE id = order.user_id   -- runs once per order!
-- Use a single JOIN or IN clause instead.

-- ❌ BAD: SELECT * in a subquery — returns all columns needlessly
SELECT * FROM orders
WHERE UserId IN (SELECT * FROM users WHERE country = 'US'); -- ❌ BAD: should be SELECT id

-- ❌ BAD: OFFSET pagination at large pages — scans all preceding rows
SELECT * FROM orders
ORDER BY ts
LIMIT 20 OFFSET 100000;   -- ❌ BAD: use keyset pagination (WHERE id > last_seen_id)

-- ❌ BAD: no index on foreign key column — full table scan on JOIN
-- (Missing: CREATE INDEX idx_orders_user_id ON orders (UserId))
