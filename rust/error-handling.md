# Rust Error Handling

---

## The Result Type

All fallible operations return `Result<T, E>`. Never use panics for expected error conditions.

## thiserror — Library Errors

```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum OrderError {
    #[error("Order {id} not found")]
    NotFound { id: String },

    #[error("Order {id} cannot be cancelled (status: {status:?})")]
    NotCancellable { id: String, status: OrderStatus },

    #[error("Database error")]
    Database(#[from] sqlx::Error),

    #[error("Payment service error")]
    Payment(#[from] PaymentError),
}
```

## anyhow — Application Code

```rust
use anyhow::{Context, Result, bail, ensure};

async fn run_server() -> Result<()> {
    let config = Config::from_env()
        .context("Failed to load configuration from environment")?;

    ensure!(config.port > 0, "Port must be positive, got {}", config.port);

    let db = Database::connect(&config.database_url)
        .await
        .context("Failed to connect to database")?;

    Ok(())
}
```

## Error Conversion with `?`

```rust
// Custom From impls allow ? to convert between error types
impl From<sqlx::Error> for OrderError {
    fn from(err: sqlx::Error) -> Self {
        OrderError::Database(err)
    }
}

// Now ? automatically converts sqlx::Error to OrderError
async fn find_order(id: &str, pool: &PgPool) -> Result<Order, OrderError> {
    let order = sqlx::query_as!(Order, "SELECT * FROM orders WHERE id = $1", id)
        .fetch_optional(pool)
        .await? // sqlx::Error → OrderError::Database via From
        .ok_or_else(|| OrderError::NotFound { id: id.to_string() })?;
    Ok(order)
}
```

## Panic Policy

| Context | `unwrap()` / `expect()` | `panic!()` |
|---------|------------------------|-----------|
| Tests | ✅ Allowed | ✅ Allowed |
| CLI entry point | ✅ With descriptive `expect()` message | ✅ For fatal config errors |
| Library code | ❌ Never | ❌ Never |
| Application business logic | ❌ Never | ❌ Never |
| Truly unreachable code | `unreachable!()` with comment | Same |

When you write `expect()`, explain what invariant has been violated:
```rust
// ✅ Descriptive expect
let config = serde_json::from_str(&raw)
    .expect("Config JSON is malformed; this should have been validated at startup");
```
