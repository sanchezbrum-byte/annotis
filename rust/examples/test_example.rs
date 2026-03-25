// Tests for good_service.rs — lives in the same module under #[cfg(test)]
// In a real project, integration tests go in tests/, unit tests are inline.

#[cfg(test)]
mod tests {
    use super::*;
    use async_trait::async_trait;
    use std::sync::{Arc, Mutex};

    // -------------------------------------------------------------------------
    // Fake implementations
    // -------------------------------------------------------------------------

    #[derive(Default)]
    struct FakeOrderRepo {
        orders: Mutex<std::collections::HashMap<String, Order>>,
        saved: Mutex<Vec<Order>>,
    }

    impl FakeOrderRepo {
        fn with_order(order: Order) -> Arc<Self> {
            let repo = Arc::new(Self::default());
            repo.orders.lock().unwrap().insert(order.id.to_string(), order);
            repo
        }
    }

    #[async_trait]
    impl OrderRepository for FakeOrderRepo {
        async fn find_by_id(&self, id: &OrderId) -> Result<Option<Order>, anyhow::Error> {
            Ok(self.orders.lock().unwrap().get(&id.to_string()).cloned())
        }

        async fn save(&self, order: &Order) -> Result<(), anyhow::Error> {
            self.saved.lock().unwrap().push(order.clone());
            Ok(())
        }
    }

    struct StubGateway {
        result: Result<String, PaymentError>,
    }

    impl StubGateway {
        fn succeeds_with(id: &str) -> Arc<Self> {
            Arc::new(Self { result: Ok(id.to_string()) })
        }

        fn declines(code: &str) -> Arc<Self> {
            Arc::new(Self {
                result: Err(PaymentError::CardDeclined { code: code.to_string() }),
            })
        }
    }

    #[async_trait]
    impl PaymentGateway for StubGateway {
        async fn charge(&self, _: u64, _: &str, _: &str) -> Result<String, PaymentError> {
            self.result.as_ref().cloned().map_err(|e| match &e {
                PaymentError::CardDeclined { code } => PaymentError::CardDeclined { code: code.clone() },
                _ => PaymentError::InvalidInput("stub error".into()),
            })
        }
    }

    // -------------------------------------------------------------------------
    // Test helpers
    // -------------------------------------------------------------------------

    fn pending_order() -> Order {
        Order {
            id: OrderId::new(),
            user_id: "user-456".to_string(),
            total_cents: 10_000,
            currency: "USD".to_string(),
            status: OrderStatus::Pending,
        }
    }

    fn make_service(
        repo: Arc<dyn OrderRepository>,
        gateway: Arc<dyn PaymentGateway>,
    ) -> OrderPaymentService {
        OrderPaymentService::new(repo, gateway)
    }

    // -------------------------------------------------------------------------
    // Tests
    // -------------------------------------------------------------------------

    #[tokio::test]
    async fn process_payment_valid_card_returns_payment_id() {
        // Arrange
        let order = pending_order();
        let repo = FakeOrderRepo::with_order(order.clone());
        let gateway = StubGateway::succeeds_with("pay-789");
        let service = make_service(repo.clone(), gateway);

        // Act
        let result = service.process_payment(&order.id, "tok_visa").await;

        // Assert
        assert_eq!(result.unwrap(), "pay-789");
        assert_eq!(repo.saved.lock().unwrap()[0].status, OrderStatus::Paid);
    }

    #[tokio::test]
    async fn process_payment_order_not_found_returns_order_not_found_error() {
        let repo = Arc::new(FakeOrderRepo::default()); // empty
        let service = make_service(repo, StubGateway::succeeds_with("pay-1"));
        let fake_id = OrderId::new();

        let err = service.process_payment(&fake_id, "tok_visa").await.unwrap_err();

        assert!(matches!(err, PaymentError::OrderNotFound(_)));
    }

    #[tokio::test]
    async fn process_payment_already_paid_returns_not_payable_error() {
        let mut order = pending_order();
        order.status = OrderStatus::Paid;
        let order_id = order.id.clone();
        let repo = FakeOrderRepo::with_order(order);

        let service = make_service(repo, StubGateway::succeeds_with("pay-1"));
        let err = service.process_payment(&order_id, "tok_visa").await.unwrap_err();

        assert!(matches!(err, PaymentError::OrderNotPayable(_, OrderStatus::Paid)));
    }

    #[tokio::test]
    async fn process_payment_gateway_declines_returns_card_declined_and_does_not_save() {
        let order = pending_order();
        let order_id = order.id.clone();
        let repo = FakeOrderRepo::with_order(order);

        let gateway = StubGateway::declines("insufficient_funds");
        let service = make_service(repo.clone(), gateway);

        let err = service.process_payment(&order_id, "tok_declined").await.unwrap_err();

        assert!(matches!(err, PaymentError::CardDeclined { .. }));
        // ✅ Data integrity: no save on failure
        assert!(repo.saved.lock().unwrap().is_empty());
    }

    #[tokio::test]
    async fn process_payment_empty_card_token_returns_invalid_input() {
        let order = pending_order();
        let order_id = order.id.clone();
        let repo = FakeOrderRepo::with_order(order);
        let service = make_service(repo, StubGateway::succeeds_with("pay-1"));

        let err = service.process_payment(&order_id, "").await.unwrap_err();

        assert!(matches!(err, PaymentError::InvalidInput(_)));
    }
}
