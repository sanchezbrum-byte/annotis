"""Payment processing use case — demonstrates clean Python style.

This module implements the ProcessPayment use case following Clean Architecture,
with proper error handling, type annotations, and documentation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from myapp.domain.exceptions import (
    InsufficientFundsError,
    PaymentDeclinedError,
    PaymentGatewayError,
)
from myapp.domain.order import Order, OrderStatus
from myapp.domain.payment import Payment, PaymentStatus

if TYPE_CHECKING:
    from myapp.domain.ports import EventBus, OrderRepository, PaymentGateway

logger = logging.getLogger(__name__)

SUPPORTED_CURRENCIES = frozenset({"USD", "EUR", "GBP", "CAD", "AUD"})


# ✅ Value object: immutable, validated, domain-expressive
@dataclass(frozen=True)
class ProcessPaymentRequest:
    """Input contract for the ProcessPayment use case."""

    order_id: str
    amount: Decimal
    currency: str
    card_token: str

    def __post_init__(self) -> None:
        if self.amount <= Decimal("0"):
            raise ValueError(f"Amount must be positive, got: {self.amount}")
        if self.currency not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {self.currency!r}")
        if not self.card_token:
            raise ValueError("card_token is required")


@dataclass(frozen=True)
class ProcessPaymentResult:
    """Successful payment result."""

    payment_id: str
    order_id: str
    amount: Decimal
    currency: str
    status: PaymentStatus


# ✅ Single responsibility: this class orchestrates one use case
class ProcessPaymentUseCase:
    """Process a payment for an existing order.

    Validates the order state, charges the customer via the payment gateway,
    persists the payment record, and publishes a domain event.

    Args:
        order_repo: Repository for loading and saving orders.
        payment_gateway: External payment processor adapter.
        event_bus: Domain event publisher.
    """

    def __init__(
        self,
        order_repo: OrderRepository,
        payment_gateway: PaymentGateway,
        event_bus: EventBus,
    ) -> None:
        self._order_repo = order_repo
        self._payment_gateway = payment_gateway
        self._event_bus = event_bus

    def execute(self, request: ProcessPaymentRequest) -> ProcessPaymentResult:
        """Execute the process payment use case.

        Args:
            request: Validated payment request containing order ID,
                amount, currency, and card token.

        Returns:
            ProcessPaymentResult with the payment ID and confirmed status.

        Raises:
            OrderNotFoundError: If the order does not exist.
            OrderNotPayableError: If the order is not in PENDING status.
            InsufficientFundsError: If the card has insufficient funds.
            PaymentDeclinedError: If the payment gateway declines the charge.
            PaymentGatewayError: If the gateway is unreachable.
        """
        # ✅ Guard clauses: validate state before any side effects
        order = self._load_and_validate_order(request.order_id, request.amount)

        # ✅ Idempotency: use stable key so retries don't double-charge
        # Stripe deduplication window is 24h; key is date-scoped.
        idempotency_key = _build_idempotency_key(request.order_id)

        logger.info(
            "Processing payment",
            extra={
                "order_id": request.order_id,
                "amount": str(request.amount),
                "currency": request.currency,
            },
        )

        payment = self._charge_gateway(request, idempotency_key)
        order.mark_paid(payment)
        self._order_repo.save(order)
        self._event_bus.publish(payment.to_paid_event())

        logger.info(
            "Payment processed successfully",
            extra={"order_id": request.order_id, "payment_id": payment.id},
        )

        return ProcessPaymentResult(
            payment_id=payment.id,
            order_id=request.order_id,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
        )

    def _load_and_validate_order(self, order_id: str, amount: Decimal) -> Order:
        """Load the order and verify it is in a payable state.

        Args:
            order_id: The order to load.
            amount: Payment amount; must match order total.

        Returns:
            The loaded Order entity.

        Raises:
            OrderNotFoundError: If no order with order_id exists.
            OrderNotPayableError: If the order is not in PENDING status.
            InsufficientFundsError: If amount < order.total.
        """
        order = self._order_repo.find(order_id)
        if order is None:
            # ✅ Explicit domain exception — not a generic KeyError
            from myapp.domain.exceptions import OrderNotFoundError
            raise OrderNotFoundError(order_id)

        if order.status != OrderStatus.PENDING:
            from myapp.domain.exceptions import OrderNotPayableError
            raise OrderNotPayableError(order_id, order.status)

        if amount < order.total:
            raise InsufficientFundsError(
                required=order.total, provided=amount
            )

        return order

    def _charge_gateway(
        self, request: ProcessPaymentRequest, idempotency_key: str
    ) -> Payment:
        """Charge the payment gateway and return the payment record.

        Translates gateway-specific errors into domain exceptions.
        """
        try:
            return self._payment_gateway.charge(
                amount=request.amount,
                currency=request.currency,
                card_token=request.card_token,
                idempotency_key=idempotency_key,
            )
        except PaymentDeclinedError:
            # ✅ Re-raise domain exception — caller handles the business case
            raise
        except Exception as exc:
            # ✅ Wrap infrastructure failure in domain exception
            logger.exception(
                "Payment gateway error",
                extra={"order_id": request.order_id},
            )
            raise PaymentGatewayError(
                "Payment service is temporarily unavailable"
            ) from exc


def _build_idempotency_key(order_id: str) -> str:
    """Build a date-scoped idempotency key for the given order.

    The key is stable within a calendar day (UTC), matching Stripe's
    24-hour deduplication window for idempotency keys.
    """
    from datetime import date
    return f"pay:{order_id}:{date.today().isoformat()}"
