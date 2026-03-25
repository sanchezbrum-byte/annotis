# Performance Standards

> **Source:** "Systems Performance" (Brendan Gregg), "Designing Data-Intensive Applications" (Kleppmann), Google SRE Book, "High Performance Browser Networking" (Grigorik)

---

## 1. The Performance Optimization Process

**Rule #1: Never optimize without measuring first.**

```
1. Identify → 2. Measure → 3. Hypothesize → 4. Change → 5. Measure again → 6. Compare
```

Do not guess at bottlenecks. Profile first, then fix the actual bottleneck. Knuth's famous quote: *"Premature optimization is the root of all evil."*

**When to optimize:**
- You have a measured performance problem (not a perceived one)
- You have an established baseline (before/after numbers)
- The optimization does not significantly increase code complexity
- The critical path has been identified via profiling

---

## 2. Big-O Complexity Awareness

**Rule:** Always comment the time and space complexity for non-trivial algorithms.

```python
def find_duplicates(items: list[int]) -> set[int]:
    """Find all duplicate values in the list.

    Time: O(n) — single pass with hash set
    Space: O(n) — worst case all elements unique, stored in seen set
    """
    seen = set()
    duplicates = set()
    for item in items:       # O(n)
        if item in seen:     # O(1) average for hash set
            duplicates.add(item)
        seen.add(item)
    return duplicates

# ❌ BAD alternative — not commented, O(n²) without obvious reason
def find_duplicates_slow(items):
    return [x for x in items if items.count(x) > 1]  # O(n²): .count() is O(n)
```

### Complexity Reference

| Operation | Data Structure | Complexity |
|-----------|---------------|-----------|
| Lookup | Hash map/set | O(1) avg, O(n) worst |
| Lookup | Sorted array (binary search) | O(log n) |
| Lookup | Unsorted array/list | O(n) |
| Insert | Hash map/set | O(1) avg |
| Insert | Balanced BST | O(log n) |
| Sort | Comparison sort (quicksort, mergesort) | O(n log n) |
| Sort | Counting/radix sort | O(n + k) |

---

## 3. Common Performance Anti-Patterns

### N+1 Query Problem
```python
# ❌ BAD: O(n) database queries for n users
orders = Order.query.all()  # 1 query
for order in orders:
    print(order.user.name)  # n queries — 1 per order

# ✅ GOOD: O(1) queries via JOIN or eager loading
orders = Order.query.options(joinedload(Order.user)).all()  # 1 query
```

### String Concatenation in Loops
```python
# ❌ BAD: O(n²) — new string allocated each iteration
result = ""
for item in large_list:
    result += str(item) + ", "

# ✅ GOOD: O(n) — join at end
result = ", ".join(str(item) for item in large_list)
```

### Repeated Expensive Computations
```python
# ❌ BAD: regex compiled on every call — O(n) compilation overhead
def validate_email(email: str) -> bool:
    return bool(re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email))

# ✅ GOOD: compiled once at module load
_EMAIL_PATTERN = re.compile(r'^[\w.-]+@[\w.-]+\.\w+$')

def validate_email(email: str) -> bool:
    return bool(_EMAIL_PATTERN.match(email))
```

### Unnecessary Data Loading
```python
# ❌ BAD: loads entire user object when only name is needed
users = User.query.all()
names = [u.name for u in users]

# ✅ GOOD: query only what you need
names = db.session.query(User.name).all()
```

---

## 4. Caching Strategy

**Cache only when:**
1. You have measured the performance problem
2. The data is read frequently and written infrequently
3. Stale data is acceptable for the use case

**Cache invalidation rules:**
- Have an explicit TTL for every cached item
- Invalidate proactively when the underlying data changes
- Never cache security-sensitive data (authorization decisions, session tokens)
- Document what is cached and why

**Cache hierarchy:**
```
1. In-process (memory) — fastest; lost on restart
2. Distributed (Redis/Memcached) — fast; survives restarts
3. CDN/Edge — for static assets and cacheable API responses
4. Database query cache — least reliable; often harmful at scale
```

---

## 5. Database Performance

- Add indexes for every column that appears in a `WHERE`, `JOIN ON`, or `ORDER BY` clause
- Use `EXPLAIN ANALYZE` (PostgreSQL) or `EXPLAIN` (MySQL) to verify query plans before releasing
- Avoid `SELECT *` — specify columns explicitly
- Use database connection pooling (PgBouncer, HikariCP) — never create a new connection per request
- Batch inserts/updates — never execute single-row inserts in a loop for bulk operations

```sql
-- ❌ BAD: 1000 separate queries
INSERT INTO events (type, user_id) VALUES ('login', 1);
INSERT INTO events (type, user_id) VALUES ('login', 2);
...

-- ✅ GOOD: single batch insert
INSERT INTO events (type, user_id) VALUES
  ('login', 1), ('login', 2), ..., ('login', 1000);
```

---

## 6. Memory Management

- Avoid loading entire large datasets into memory — use streaming/pagination
- Be aware of memory leaks in long-running processes: unclosed file handles, growing caches without eviction, event listener leaks
- For large file processing: stream, don't load
- Use memory profilers (memory_profiler for Python, heapster for Go, Chrome DevTools for JS) before claiming a memory optimization is needed

---

## 7. Concurrency Performance

- **Thread pools**: size for CPU-bound work = # of CPU cores; size for I/O-bound work = 10–100x CPU cores
- **Async/await** is appropriate for I/O-bound concurrency (network, disk), not CPU-bound
- Use **connection pools** for any external resource (database, HTTP client, Redis)
- Measure actual throughput and latency under realistic concurrent load before declaring a performance target met

---

## 8. Frontend Performance (Web)

- Target: Core Web Vitals — LCP < 2.5s, FID < 100ms, CLS < 0.1
- Minimize main-thread JavaScript — parse + compile cost scales with bundle size
- Lazy-load below-the-fold images and non-critical components
- Use `content-encoding: gzip` or `br` for all text responses
- Set proper cache headers: `Cache-Control: max-age=31536000, immutable` for content-hashed assets

---

## 9. Service Level Objectives (SLOs)

Define measurable performance targets per service:

| Metric | Good Target | Alert Threshold |
|--------|------------|----------------|
| P50 latency | < 50ms | > 100ms |
| P99 latency | < 200ms | > 500ms |
| P99.9 latency | < 1000ms | > 2000ms |
| Error rate | < 0.1% | > 1% |
| Availability | > 99.9% | < 99.5% |

Measure at the 50th, 95th, and 99th percentile — averages hide tail latency problems.
