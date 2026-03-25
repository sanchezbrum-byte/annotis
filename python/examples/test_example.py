"""Tests for ProcessPaymentUseCase — demonstrates pytest best practices.

Test naming: test_<method>_<scenario>_<expected_behavior>
Pattern: AAA (Arrange-Act-Assert)
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, call

import pytest

from myapp.application.process_payment import (
    ProcessPaymentRequest,
    ProcessPaymentResult,
    ProcessPaymentUseCase,
)
from myapp.domain.exceptions import (
    InsufficientFundsError,
    OrderNotFoundError,
    OrderNotPayableError,
    PaymentDeclinedError,
    PaymentGatewayError,
)
from myapp.domain.order import OrderStatus
from tests.factories import OrderFactory, PaymentFactory


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def order_repo():
    return MagicMock()


@pytest.fixture
def payment_gateway():
    return MagicMock()


@pytest.fixture
def event_bus():
    return MagicMock()


@pytest.fixture
def use_case(order_repo, payment_gateway, event_bus):
    return ProcessPaymentUseCase(
        order_repo=order_repo,
        payment_gateway=payment_gateway,
        event_bus=event_bus,
    )


@pytest.fixture
def pending_order():
    return OrderFactory.build(
        id="order-123",
        total=Decimal("100.00"),
        status=OrderStatus.PENDING,
    )


@pytest.fixture
def valid_request():
    return ProcessPaymentRequest(
        order_id="order-123",
        amount=Decimal("100.00"),
        currency="USD",
        card_token="tok_visa",
    )


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_execute_with_valid_request_returns_payment_result(
    use_case, order_repo, payment_gateway, event_bus, pending_order, valid_request
):
    # Arrange
    order_repo.find.return_value = pending_order
    expected_payment = PaymentFactory.build(
        order_id="order-123",
        amount=Decimal("100.00"),
        currency="USD",
    )
    payment_gateway.charge.return_value = expected_payment

    # Act
    result = use_case.execute(valid_request)

    # Assert
    assert isinstance(result, ProcessPaymentResult)
    assert result.order_id == "order-123"
    assert result.amount == Decimal("100.00")
    assert result.payment_id == expected_payment.id


def test_execute_saves_order_after_successful_charge(
    use_case, order_repo, payment_gateway, pending_order, valid_request
):
    # Arrange
    order_repo.find.return_value = pending_order
    payment_gateway.charge.return_value = PaymentFactory.build()

    # Act
    use_case.execute(valid_request)

    # Assert — order is saved exactly once
    order_repo.save.assert_called_once_with(pending_order)


def test_execute_publishes_payment_event_after_successful_charge(
    use_case, order_repo, payment_gateway, event_bus, pending_order, valid_request
):
    # Arrange
    order_repo.find.return_value = pending_order
    payment = PaymentFactory.build()
    payment_gateway.charge.return_value = payment

    # Act
    use_case.execute(valid_request)

    # Assert — domain event published
    event_bus.publish.assert_called_once_with(payment.to_paid_event())


# ---------------------------------------------------------------------------
# Order validation failures
# ---------------------------------------------------------------------------


def test_execute_when_order_not_found_raises_order_not_found_error(
    use_case, order_repo, valid_request
):
    # Arrange
    order_repo.find.return_value = None

    # Act / Assert
    with pytest.raises(OrderNotFoundError):
        use_case.execute(valid_request)


def test_execute_when_order_already_paid_raises_order_not_payable_error(
    use_case, order_repo, valid_request
):
    # Arrange
    paid_order = OrderFactory.build(status=OrderStatus.PAID)
    order_repo.find.return_value = paid_order

    # Act / Assert
    with pytest.raises(OrderNotPayableError):
        use_case.execute(valid_request)


def test_execute_when_amount_less_than_total_raises_insufficient_funds(
    use_case, order_repo, pending_order
):
    # Arrange
    order_repo.find.return_value = pending_order  # total = 100.00
    request = ProcessPaymentRequest(
        order_id="order-123",
        amount=Decimal("50.00"),  # ← less than total
        currency="USD",
        card_token="tok_visa",
    )

    # Act / Assert
    with pytest.raises(InsufficientFundsError):
        use_case.execute(request)


# ---------------------------------------------------------------------------
# Gateway failures
# ---------------------------------------------------------------------------


def test_execute_when_card_declined_raises_payment_declined_error(
    use_case, order_repo, payment_gateway, pending_order, valid_request
):
    # Arrange
    order_repo.find.return_value = pending_order
    payment_gateway.charge.side_effect = PaymentDeclinedError("insufficient_funds")

    # Act / Assert
    with pytest.raises(PaymentDeclinedError):
        use_case.execute(valid_request)


def test_execute_when_gateway_unavailable_raises_payment_gateway_error(
    use_case, order_repo, payment_gateway, pending_order, valid_request
):
    # Arrange
    order_repo.find.return_value = pending_order
    payment_gateway.charge.side_effect = ConnectionError("Connection refused")

    # Act / Assert
    with pytest.raises(PaymentGatewayError):
        use_case.execute(valid_request)


def test_execute_when_gateway_fails_does_not_save_order(
    use_case, order_repo, payment_gateway, pending_order, valid_request
):
    # Arrange — gateway fails
    order_repo.find.return_value = pending_order
    payment_gateway.charge.side_effect = ConnectionError("timeout")

    # Act
    with pytest.raises(PaymentGatewayError):
        use_case.execute(valid_request)

    # Assert — order is NOT saved when payment fails (data integrity)
    order_repo.save.assert_not_called()


# ---------------------------------------------------------------------------
# Input validation (corner cases)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "amount,currency,card_token,expected_error",
    [
        (Decimal("0.00"), "USD", "tok_visa", "Amount must be positive"),
        (Decimal("-1.00"), "USD", "tok_visa", "Amount must be positive"),
        (Decimal("10.00"), "XYZ", "tok_visa", "Unsupported currency"),
        (Decimal("10.00"), "", "tok_visa", "Unsupported currency"),
        (Decimal("10.00"), "USD", "", "card_token is required"),
    ],
)
def test_process_payment_request_with_invalid_input_raises_value_error(
    amount, currency, card_token, expected_error
):
    with pytest.raises(ValueError, match=expected_error):
        ProcessPaymentRequest(
            order_id="order-123",
            amount=amount,
            currency=currency,
            card_token=card_token,
        )
