# Rust AI Rules

> Full reference: `rust/style-guide.md`

---

## Formatting (rustfmt)

- Line limit: **100 chars** (`max_width = 100`)
- Indentation: **4 spaces**
- Use `cargo fmt` — no manual formatting debates
- Import grouping: std → external → local (rustfmt manages)

## Naming (Rust API Guidelines)

| Concept | Style | Example |
|---------|-------|---------|
| Functions/methods | `snake_case` | `process_payment`, `find_by_id` |
| Types (struct/enum/trait) | `PascalCase` | `Order`, `PaymentError` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_RETRIES` |
| Modules | `snake_case` | `order_service`, `payment_gateway` |
| Conversion methods | `from_`, `into_`, `to_`, `as_` | `Order::from_row`, `to_string` |

## Error Handling

```rust
// ✅ thiserror for library errors
#[derive(Debug, Error)]
pub enum PaymentError {
    #[error("Order {0} not found")] OrderNotFound(String),
    #[error("Card declined: {code}")] Declined { code: String },
    #[error("Service unavailable")] ServiceUnavailable(#[source] reqwest::Error),
}

// ✅ anyhow for application error propagation
use anyhow::{Context, Result};
let config = Config::from_env().context("Failed to load config")?;

// ❌ NEVER unwrap/expect in library code
let order = repo.find(id).unwrap(); // panics → crashes caller
```

## Ownership Patterns

```rust
// ✅ Pass by reference for read-only
fn log_order(order: &Order) { ... }

// ✅ Pass by value + move for ownership transfer
fn process(order: Order) { ... }

// ✅ Arc<RwLock<T>> for shared mutable state in async
let state = Arc::new(RwLock::new(AppState::default()));
```

## Unsafe Code

Every `unsafe` block MUST have a `// SAFETY:` comment:
```rust
// SAFETY: pointer was created by Box::into_raw, exclusive access guaranteed
let value = unsafe { Box::from_raw(ptr) };
```

## panic! Policy

| Context | `unwrap()`/`panic!()` |
|---------|-----------------------|
| Tests | ✅ Allowed |
| CLI entry point | ✅ With descriptive `expect()` message |
| Library code | ❌ Never — return `Result` |
| Business logic | ❌ Never |

## Security

```rust
// ✅ Parameterized SQL (sqlx)
let user = sqlx::query_as!(User, "SELECT * FROM users WHERE email = $1", email)
    .fetch_optional(&pool).await?;

// ✅ Secrets from environment
let db_url = std::env::var("DATABASE_URL")
    .expect("DATABASE_URL must be set");
```

## Tooling

```bash
cargo fmt                    # format
cargo clippy -- -D warnings  # lint (deny all warnings)
cargo test                   # test
cargo audit                  # security scan (cargo-audit)
cargo tarpaulin              # coverage
```
