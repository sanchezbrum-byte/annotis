# Rust Style Guide

> **Sources:** The Rust API Guidelines (rust-lang.github.io/api-guidelines), rustfmt (the official Rust formatter), Clippy lint categories (github.com/rust-lang/rust-clippy), "Programming Rust" (Blandy & Orendorff)

---

## A. Formatting & Style

**Use rustfmt for all formatting.** Never manually format Rust code.

### Line Length

**100 characters** — rustfmt default (`max_width = 100` in `rustfmt.toml`).

### Indentation

**4 spaces** — Rust official style (rustfmt default).

### Trailing Commas

Use trailing commas in multi-line constructs (rustfmt enforces):

```rust
let config = Config {
    host: "localhost".to_string(),
    port: 5432,
    max_connections: 10,  // trailing comma
};
```

### Import Ordering

rustfmt groups and sorts imports automatically. Logical grouping:

```rust
// Standard library
use std::collections::HashMap;
use std::sync::Arc;

// External crates (blank line)
use axum::{extract::Path, routing::get, Router};
use serde::{Deserialize, Serialize};
use tokio::sync::RwLock;

// Local modules (blank line)
use crate::domain::order::Order;
use crate::infrastructure::db::Database;
```

### Clippy Configuration

```toml
# .clippy.toml or in Cargo.toml
[lints.clippy]
pedantic = "warn"
nursery = "warn"

# Specific lints to deny
must_use_candidate = "warn"
missing_errors_doc = "warn"
```

---

## B. Naming Conventions (Rust API Guidelines N-*)

| Concept | Convention | Example |
|---------|-----------|---------|
| Functions / methods | `snake_case` | `process_order`, `find_by_id` |
| Variables | `snake_case` | `order_id`, `total_price` |
| Modules | `snake_case` | `order_service`, `payment_gateway` |
| Types (struct, enum, trait) | `PascalCase` | `Order`, `PaymentError`, `OrderRepository` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT_MS` |
| Type parameters | `PascalCase` (single letter or descriptive) | `T`, `E`, `TItem` |
| Lifetime parameters | `'a`, `'b`, or descriptive `'cx` | `'a`, `'repo` |

### Conversion Methods (API Guidelines C-CONV)

```rust
// from/into — infallible, lossless conversions
impl From<UserId> for String { ... }

// try_from/try_into — fallible conversions
impl TryFrom<String> for EmailAddress {
  type Error = InvalidEmailError;
  fn try_from(value: String) -> Result<Self, Self::Error> { ... }
}

// to_xxx — expensive or lossy conversions
fn to_lowercase(&self) -> String { ... }

// as_xxx — cheap conversions, borrowing
fn as_str(&self) -> &str { ... }

// into_xxx — consuming conversions
fn into_inner(self) -> T { ... }
```

### Boolean Methods (API Guidelines C-PRED)

```rust
fn is_empty(&self) -> bool { ... }
fn has_subscription(&self) -> bool { ... }
fn can_be_cancelled(&self) -> bool { ... }
```

---

## C. Functions & Methods

### Single Responsibility

```rust
// ❌ BAD: function does parsing + business logic + persistence
async fn register_user(email: &str, password: &str) -> Result<User, AppError> {
    let email = parse_email(email)?;
    let hash = hash_password(password);
    let user = db.insert(email, hash).await?;
    send_welcome_email(&user).await?; // side effect mixed in
    metrics.increment("user.registered");
    Ok(user)
}

// ✅ GOOD: each concern is a separate function / called by an orchestrator
pub async fn register_user(
    email: &str,
    password: &str,
    db: &UserRepository,
    mailer: &dyn Mailer,
) -> Result<User, RegistrationError> {
    let email = EmailAddress::try_from(email.to_string())?;
    let password_hash = hash_password(password);
    let user = db.create(email, password_hash).await?;
    // Caller (use case) decides whether to send email
    Ok(user)
}
```

### Early Returns with `?`

```rust
// ✅ GOOD: early returns with ? operator — flat, readable
pub async fn process_payment(
    order_id: &OrderId,
    card_token: &str,
    repo: &dyn OrderRepository,
    gateway: &dyn PaymentGateway,
) -> Result<PaymentConfirmation, PaymentError> {
    let order = repo.find_by_id(order_id).await?
        .ok_or(PaymentError::OrderNotFound(order_id.clone()))?;

    if order.status != OrderStatus::Pending {
        return Err(PaymentError::OrderNotPayable(order.status));
    }

    let payment = gateway.charge(order.total, card_token).await?;
    repo.update_status(order_id, OrderStatus::Paid).await?;

    Ok(PaymentConfirmation::from(payment))
}
```

---

## D. Comments & Documentation

### Doc Comments (Required for all public items)

```rust
/// Process a payment for an existing pending order.
///
/// Validates the order state, charges the payment gateway, and transitions
/// the order to `Paid` status. Publishes a `PaymentProcessedEvent`.
///
/// # Arguments
///
/// * `order_id` - The ID of the order to process.
/// * `card_token` - Tokenized card from the payment provider.
///
/// # Returns
///
/// A `PaymentConfirmation` with the payment ID and status.
///
/// # Errors
///
/// Returns `PaymentError::OrderNotFound` if the order does not exist.
/// Returns `PaymentError::AlreadyPaid` if the order is not in `Pending` status.
/// Returns `PaymentError::Declined` with the decline code if the card is declined.
///
/// # Examples
///
/// ```rust
/// let confirmation = process_payment(&order_id, "tok_visa", &repo, &gateway).await?;
/// println!("Payment ID: {}", confirmation.payment_id);
/// ```
pub async fn process_payment(...) -> Result<PaymentConfirmation, PaymentError> {
```

### Safety Comments for `unsafe`

Every `unsafe` block MUST have a `// SAFETY:` comment explaining why the code is safe:

```rust
// SAFETY: We have exclusive access to this pointer because it was obtained
// from Box::into_raw() in the calling function, and the pointer has not
// been aliased elsewhere.
let value = unsafe { Box::from_raw(ptr) };
```

---

## E. Error Handling

See [error-handling.md](error-handling.md) for the full guide.

```rust
// ✅ Use thiserror for library errors
use thiserror::Error;

#[derive(Debug, Error)]
pub enum PaymentError {
    #[error("Order {0} not found")]
    OrderNotFound(OrderId),
    #[error("Order is not payable (current status: {0:?})")]
    OrderNotPayable(OrderStatus),
    #[error("Card declined: {code}")]
    Declined { code: String },
    #[error("Payment service unavailable")]
    ServiceUnavailable(#[source] reqwest::Error),
}

// ✅ Use anyhow for application-level error handling
use anyhow::{Context, Result};

async fn run() -> Result<()> {
    let config = Config::from_env()
        .context("Failed to load application configuration")?;
    // ...
    Ok(())
}
```

### Never `panic!` in Library Code

```rust
// ❌ BAD: panics in library code crash the caller's program
pub fn parse_order_id(s: &str) -> OrderId {
    OrderId(s.parse::<u64>().unwrap()) // panics on invalid input

// ✅ GOOD: return Result and let caller decide
pub fn parse_order_id(s: &str) -> Result<OrderId, ParseOrderIdError> {
    let id = s.parse::<u64>().map_err(ParseOrderIdError::InvalidFormat)?;
    Ok(OrderId(id))
}
```

---

## F. Security

### Secrets

```rust
// ❌ BAD: hardcoded secret
const DB_PASSWORD: &str = "hunter2";

// ✅ GOOD: from environment
use std::env;
let db_password = env::var("DB_PASSWORD")
    .expect("DB_PASSWORD environment variable must be set");
```

### SQL Injection — Use sqlx

```rust
// ❌ BAD: format! in SQL query — SQL injection
let query = format!("SELECT * FROM users WHERE email = '{}'", email);

// ✅ GOOD: sqlx parameterized queries
let user = sqlx::query_as!(User,
    "SELECT * FROM users WHERE email = $1",
    email
)
.fetch_optional(&pool)
.await?;
```
