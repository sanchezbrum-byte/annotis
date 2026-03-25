# Rust Performance

---

## Profiling First

```bash
# Flamegraph with cargo-flamegraph
cargo install flamegraph
cargo flamegraph --bin myapp

# Criterion benchmarks
cargo bench

# Heaptrack for allocations
heaptrack target/release/myapp
```

## Allocation Patterns

```rust
// ❌ BAD: allocates a new String on every call
fn get_greeting(name: &str) -> String {
    format!("Hello, {}!", name)
}

// ✅ GOOD: use Cow to avoid allocation when possible
use std::borrow::Cow;

fn get_greeting(name: &str) -> Cow<'static, str> {
    if name == "World" {
        Cow::Borrowed("Hello, World!")  // no allocation
    } else {
        Cow::Owned(format!("Hello, {}!", name))
    }
}

// ✅ GOOD: pre-allocate with_capacity
let mut buffer = String::with_capacity(estimated_size);
for item in &items {
    buffer.push_str(&item.to_string());
}
```

## Async Performance

```rust
// ✅ Use tokio::join! for parallel async operations
async fn get_dashboard(user_id: &UserId) -> Result<Dashboard, AppError> {
    let (user, orders, notifications) = tokio::try_join!(
        user_repo.find_by_id(user_id),
        order_repo.find_by_user(user_id),
        notification_service.get_unread(user_id),
    )?;
    Ok(Dashboard { user, orders, notifications })
}
```

## Big-O Comments

```rust
/// Find all duplicate elements in a slice.
///
/// # Complexity
///
/// Time: O(n) — single pass with a HashSet
/// Space: O(n) — HashSet grows to at most n elements
pub fn find_duplicates<T: Eq + Hash + Clone>(items: &[T]) -> Vec<T> { ... }
```
