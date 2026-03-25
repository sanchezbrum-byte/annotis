//! Order payment processing — demonstrates idiomatic Rust patterns.
//!
//! Covered patterns:
//! - `thiserror` for typed, composable errors
//! - Traits for dependency injection (testable)
//! - `async fn` with `tokio`
//! - Newtype for validated value objects
//! - `?` operator for clean error propagation

use std::fmt;
use async_trait::async_trait;
use thiserror::Error;
use uuid::Uuid;

// ✅ Newtype wraps String — prevents mixing order IDs with user IDs at compile time
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct OrderId(Uuid);

impl OrderId {
    pub fn new() -> Self {
        Self(Uuid::new_v4())
    }

    pub fn from_str(s: &str) -> Result<Self, PaymentError> {
        Uuid::parse_str(s)
            .map(Self)
            .map_err(|_| PaymentError::InvalidInput("orderId must be a valid UUID".into()))
    }
}

impl fmt::Display for OrderId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

// ✅ thiserror generates std::error::Error impl — no manual boilerplate
#[derive(Debug, Error)]
pub enum PaymentError {
    #[error("order {0} not found")]
    OrderNotFound(OrderId),

    #[error("order {0} is not payable (status: {1:?})")]
    OrderNotPayable(OrderId, OrderStatus),

    #[error("card declined: {code}")]
    CardDeclined { code: String },

    #[error("payment service unavailable: {0}")]
    ServiceUnavailable(#[source] anyhow::Error),

    #[error("invalid input: {0}")]
    InvalidInput(String),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum OrderStatus {
    Pending,
    Paid,
    Cancelled,
}

#[derive(Debug, Clone)]
pub struct Order {
    pub id: OrderId,
    pub user_id: String,
    pub total_cents: u64,
    pub currency: String,
    pub status: OrderStatus,
}

// ✅ Trait for DI — impl can be swapped for a fake in tests
#[async_trait]
pub trait OrderRepository: Send + Sync {
    async fn find_by_id(&self, id: &OrderId) -> Result<Option<Order>, anyhow::Error>;
    async fn save(&self, order: &Order) -> Result<(), anyhow::Error>;
}

#[async_trait]
pub trait PaymentGateway: Send + Sync {
    async fn charge(
        &self,
        amount_cents: u64,
        currency: &str,
        card_token: &str,
    ) -> Result<String, PaymentError>;
}

// ✅ Service owns trait objects via Arc — shared, thread-safe
pub struct OrderPaymentService {
    orders: std::sync::Arc<dyn OrderRepository>,
    gateway: std::sync::Arc<dyn PaymentGateway>,
}

impl OrderPaymentService {
    pub fn new(
        orders: std::sync::Arc<dyn OrderRepository>,
        gateway: std::sync::Arc<dyn PaymentGateway>,
    ) -> Self {
        Self { orders, gateway }
    }

    /// Process a payment for an existing pending order.
    ///
    /// Returns the payment confirmation ID on success.
    pub async fn process_payment(
        &self,
        order_id: &OrderId,
        card_token: &str,
    ) -> Result<String, PaymentError> {
        if card_token.is_empty() {
            return Err(PaymentError::InvalidInput("card_token must not be empty".into()));
        }

        // ✅ `?` propagates errors without manual match — wraps via From
        let order = self
            .orders
            .find_by_id(order_id)
            .await
            .map_err(|e| PaymentError::ServiceUnavailable(e))?
            .ok_or_else(|| PaymentError::OrderNotFound(order_id.clone()))?;

        if order.status != OrderStatus::Pending {
            return Err(PaymentError::OrderNotPayable(order_id.clone(), order.status.clone()));
        }

        let payment_id = self
            .gateway
            .charge(order.total_cents, &order.currency, card_token)
            .await?;

        // ✅ Only persist after payment succeeds
        let paid_order = Order { status: OrderStatus::Paid, ..order };
        self.orders
            .save(&paid_order)
            .await
            .map_err(|e| PaymentError::ServiceUnavailable(e))?;

        Ok(payment_id)
    }
}
