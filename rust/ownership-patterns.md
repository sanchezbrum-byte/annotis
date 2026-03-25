# Rust Ownership Patterns

---

## Ownership Rules (The Rust Book)

1. Each value has a single owner
2. When the owner goes out of scope, the value is dropped
3. There can be multiple immutable references OR one mutable reference — never both simultaneously

## Common Ownership Patterns

### Cloning vs Borrowing

```rust
// ❌ BAD: unnecessary clone — borrow instead
fn get_order_id(order: Order) -> String {
    order.id.clone() // takes ownership of order just to clone one field
}

// ✅ GOOD: borrow the order
fn get_order_id(order: &Order) -> &str {
    &order.id // returns a reference with same lifetime as order
}

// ✅ Or: if you need owned String
fn get_order_id(order: &Order) -> String {
    order.id.clone() // only clones the String, not the whole Order
}
```

### Interior Mutability with Arc<RwLock<T>>

```rust
// Shared mutable state in async code
use std::sync::Arc;
use tokio::sync::RwLock;

#[derive(Clone)]
pub struct AppState {
    pub cache: Arc<RwLock<HashMap<String, Order>>>,
}

async fn get_cached_order(state: &AppState, id: &str) -> Option<Order> {
    let cache = state.cache.read().await;
    cache.get(id).cloned()
}

async fn cache_order(state: &AppState, order: Order) {
    let mut cache = state.cache.write().await;
    cache.insert(order.id.clone(), order);
}
```

### Newtype Pattern for Domain Types

```rust
// Newtype pattern: prevents mixing up IDs
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct OrderId(pub String);

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct UserId(pub String);

// Now you can't accidentally pass a UserId where an OrderId is expected
fn find_order(id: OrderId) -> Option<Order> { ... }

let user_id = UserId("user-1".to_string());
find_order(user_id); // ❌ compile error — type mismatch
```

### Cow<str> for Flexible String APIs

```rust
use std::borrow::Cow;

// ✅ Accepts both &str and String without requiring clone
fn validate_email(email: impl Into<Cow<'static, str>>) -> Result<EmailAddress, Error> {
    let email = email.into();
    // validate...
}
```
