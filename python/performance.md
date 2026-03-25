# Python Performance

## Profiling First

```bash
# CPU profiling with cProfile
python -m cProfile -o profile.stats -s cumulative myapp/script.py
python -m pstats profile.stats

# Line-level profiling with line_profiler
pip install line_profiler
@profile  # decorator from line_profiler
def my_slow_function():
    ...
kernprof -l -v script.py

# Memory profiling
pip install memory-profiler
python -m memory_profiler script.py
```

## Async I/O for Network-Bound Code

```python
import asyncio
import httpx

# ❌ BAD: synchronous — one request at a time
def fetch_all_users(user_ids: list[str]) -> list[dict]:
    results = []
    for uid in user_ids:
        response = httpx.get(f"/users/{uid}")  # blocks for each request
        results.append(response.json())
    return results

# ✅ GOOD: async — concurrent requests
async def fetch_all_users(user_ids: list[str]) -> list[dict]:
    async with httpx.AsyncClient() as client:
        tasks = [client.get(f"/users/{uid}") for uid in user_ids]
        responses = await asyncio.gather(*tasks)  # concurrent
        return [r.json() for r in responses]
```

## Key Anti-Patterns

```python
# ❌ BAD: building large string in loop
csv = ""
for row in rows:
    csv += f"{row.id},{row.name}\n"  # O(n²) copies

# ✅ GOOD:
csv = "\n".join(f"{row.id},{row.name}" for row in rows)

# ❌ BAD: loading all rows into memory
all_orders = Order.query.all()  # millions of rows

# ✅ GOOD: stream via yield_per
for order in Order.query.yield_per(1000):
    process(order)

# ❌ BAD: repeated dict lookups
for _ in range(1_000_000):
    x = some_dict["key"]  # attribute lookup repeated

# ✅ GOOD: cache the value
value = some_dict["key"]
for _ in range(1_000_000):
    x = value
```

## slots for High-Volume Objects

```python
# For classes instantiated millions of times (e.g., events, value objects)
@dataclass(frozen=True, slots=True)
class OrderItem:
    product_id: str
    quantity: int
    unit_price: Decimal
# __slots__ reduces memory by ~40% and speeds attribute access
```
