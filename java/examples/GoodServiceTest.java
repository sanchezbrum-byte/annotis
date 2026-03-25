package com.example.orders.application;

import com.example.orders.domain.Order;
import com.example.orders.domain.OrderStatus;
import com.example.orders.domain.exceptions.OrderNotFoundException;
import com.example.orders.domain.exceptions.OrderNotPayableException;
import com.example.orders.domain.exceptions.PaymentDeclinedException;
import com.example.orders.domain.exceptions.PaymentServiceException;
import com.example.orders.domain.ports.OrderRepository;
import com.example.orders.domain.ports.PaymentGateway;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;

import java.math.BigDecimal;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

/**
 * Unit tests for {@link OrderPaymentService}.
 *
 * <p>Uses Mockito for gateway + repository fakes, AssertJ for fluent assertions.
 * Each test follows the Arrange → Act → Assert pattern.
 */
class OrderPaymentServiceTest {

  // ✅ Mocks declared at class level, re-initialised per test
  private OrderRepository orderRepository;
  private PaymentGateway paymentGateway;
  private OrderPaymentService service;

  @BeforeEach
  void setUp() {
    orderRepository = mock(OrderRepository.class);
    paymentGateway = mock(PaymentGateway.class);
    service = new OrderPaymentService(orderRepository, paymentGateway);
  }

  // ---------------------------------------------------------------------------
  // Helper builders
  // ---------------------------------------------------------------------------

  private Order buildPendingOrder(String orderId) {
    return Order.builder()
        .id(orderId)
        .userId("user-456")
        .total(new BigDecimal("100.00"))
        .currency("USD")
        .status(OrderStatus.PENDING)
        .build();
  }

  // ---------------------------------------------------------------------------
  // Happy path
  // ---------------------------------------------------------------------------

  @Nested
  @DisplayName("Given a valid pending order and successful payment")
  class HappyPath {

    @Test
    @DisplayName("should return payment ID and mark order as PAID")
    void processPayment_validCard_returnsPaymentId() {
      // Arrange
      Order order = buildPendingOrder("order-123");
      when(orderRepository.findById("order-123")).thenReturn(Optional.of(order));
      when(paymentGateway.charge(any(), anyString(), anyString())).thenReturn("pay-789");

      // Act
      String paymentId = service.processPayment("order-123", "tok_visa");

      // Assert
      assertThat(paymentId).isEqualTo("pay-789");
      verify(orderRepository).save(order);
      assertThat(order.getStatus()).isEqualTo(OrderStatus.PAID);
    }
  }

  // ---------------------------------------------------------------------------
  // Input validation
  // ---------------------------------------------------------------------------

  @Nested
  @DisplayName("Input validation")
  class Validation {

    @ParameterizedTest(name = "orderId = [{0}]")
    @NullAndEmptySource
    @ValueSource(strings = {"  "})
    @DisplayName("should reject blank or null orderId")
    void processPayment_blankOrderId_throwsIllegalArgument(String orderId) {
      assertThatThrownBy(() -> service.processPayment(orderId, "tok_visa"))
          .isInstanceOf(IllegalArgumentException.class);
      verifyNoInteractions(orderRepository, paymentGateway);
    }

    @ParameterizedTest(name = "cardToken = [{0}]")
    @NullAndEmptySource
    @ValueSource(strings = {"  "})
    @DisplayName("should reject blank or null cardToken")
    void processPayment_blankCardToken_throwsIllegalArgument(String cardToken) {
      assertThatThrownBy(() -> service.processPayment("order-123", cardToken))
          .isInstanceOf(IllegalArgumentException.class);
      verifyNoInteractions(orderRepository, paymentGateway);
    }
  }

  // ---------------------------------------------------------------------------
  // Order state errors
  // ---------------------------------------------------------------------------

  @Nested
  @DisplayName("Order state errors")
  class OrderStateErrors {

    @Test
    @DisplayName("should throw OrderNotFoundException when order does not exist")
    void processPayment_orderNotFound_throwsOrderNotFoundException() {
      when(orderRepository.findById(anyString())).thenReturn(Optional.empty());

      assertThatThrownBy(() -> service.processPayment("missing-id", "tok_visa"))
          .isInstanceOf(OrderNotFoundException.class);
      verifyNoInteractions(paymentGateway);
    }

    @Test
    @DisplayName("should throw OrderNotPayableException when order is already PAID")
    void processPayment_alreadyPaid_throwsOrderNotPayableException() {
      Order paidOrder = buildPendingOrder("order-123");
      paidOrder.setStatus(OrderStatus.PAID);
      when(orderRepository.findById("order-123")).thenReturn(Optional.of(paidOrder));

      assertThatThrownBy(() -> service.processPayment("order-123", "tok_visa"))
          .isInstanceOf(OrderNotPayableException.class);
      verifyNoInteractions(paymentGateway);
    }
  }

  // ---------------------------------------------------------------------------
  // Gateway failures
  // ---------------------------------------------------------------------------

  @Nested
  @DisplayName("Gateway failures")
  class GatewayFailures {

    @Test
    @DisplayName("should propagate PaymentDeclinedException and NOT save order")
    void processPayment_cardDeclined_throwsDeclinedException() {
      Order order = buildPendingOrder("order-123");
      when(orderRepository.findById("order-123")).thenReturn(Optional.of(order));
      when(paymentGateway.charge(any(), anyString(), anyString()))
          .thenThrow(new PaymentDeclinedException("insufficient_funds"));

      assertThatThrownBy(() -> service.processPayment("order-123", "tok_declined"))
          .isInstanceOf(PaymentDeclinedException.class);

      // ✅ Data integrity: order must not be saved in failed state
      verify(orderRepository, never()).save(any());
      assertThat(order.getStatus()).isEqualTo(OrderStatus.PENDING);
    }

    @Test
    @DisplayName("should wrap unexpected gateway errors in PaymentServiceException")
    void processPayment_gatewayUnavailable_throwsPaymentServiceException() {
      Order order = buildPendingOrder("order-123");
      when(orderRepository.findById("order-123")).thenReturn(Optional.of(order));
      when(paymentGateway.charge(any(), anyString(), anyString()))
          .thenThrow(new RuntimeException("connection refused"));

      assertThatThrownBy(() -> service.processPayment("order-123", "tok_visa"))
          .isInstanceOf(PaymentServiceException.class)
          .hasCauseInstanceOf(RuntimeException.class);
    }
  }
}
