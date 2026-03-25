# Rust Testing Standards

---

## Unit Tests (in-module, bottom of file)

```rust
// src/domain/order.rs

pub fn calculate_total(items: &[OrderItem]) -> Decimal {
    items.iter().map(|i| i.unit_price * Decimal::from(i.quantity)).sum()
}

#[cfg(test)]
mod tests {
    use super::*;
    use rust_decimal_macros::dec;

    #[test]
    fn calculate_total_with_multiple_items_returns_correct_sum() {
        // Arrange
        let items = vec![
            OrderItem { unit_price: dec!(10.00), quantity: 2 },
            OrderItem { unit_price: dec!(5.50), quantity: 1 },
        ];

        // Act
        let total = calculate_total(&items);

        // Assert
        assert_eq!(total, dec!(25.50));
    }

    #[test]
    fn calculate_total_with_empty_items_returns_zero() {
        assert_eq!(calculate_total(&[]), Decimal::ZERO);
    }
}
```

## Integration Tests (tests/ directory)

```rust
// tests/order_repository_test.rs
use sqlx::PgPool;
use testcontainers::clients::Cli;
use testcontainers_modules::postgres::Postgres;

#[sqlx::test]
async fn save_and_find_order_by_id_returns_saved_order(pool: PgPool) {
    let repo = PostgresOrderRepository::new(pool);
    let order = Order::new(OrderId::new(), UserId::new(), vec![]);

    repo.save(&order).await.unwrap();
    let found = repo.find_by_id(&order.id).await.unwrap();

    assert!(found.is_some());
    assert_eq!(found.unwrap().id, order.id);
}
```

## Async Tests

```rust
#[tokio::test]
async fn process_payment_with_valid_card_returns_confirmation() {
    let mut mock_gateway = MockPaymentGateway::new();
    mock_gateway
        .expect_charge()
        .returning(|_, _| Ok(Payment { id: "pay-123".into(), ..Default::default() }));

    let result = process_payment(&order_id, "tok_visa", &repo, &mock_gateway).await;

    assert!(result.is_ok());
    assert_eq!(result.unwrap().payment_id, "pay-123");
}
```

## Property-Based Testing with proptest

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn calculate_total_never_negative(
        prices in prop::collection::vec(0.01f64..1000.0f64, 0..100),
        quantities in prop::collection::vec(1u32..100u32, 0..100)
    ) {
        // Align lengths
        let min_len = prices.len().min(quantities.len());
        let items: Vec<OrderItem> = prices[..min_len].iter()
            .zip(quantities[..min_len].iter())
            .map(|(&p, &q)| OrderItem { unit_price: Decimal::try_from(p).unwrap(), quantity: q })
            .collect();

        let total = calculate_total(&items);
        prop_assert!(total >= Decimal::ZERO);
    }
}
```

## Cargo.toml for Testing

```toml
[dev-dependencies]
tokio = { version = "1", features = ["macros", "rt-multi-thread"] }
mockall = "0.13"
proptest = "1"
sqlx = { version = "0.8", features = ["test-utils"] }
testcontainers = "0.23"
testcontainers-modules = { version = "0.11", features = ["postgres"] }
```
