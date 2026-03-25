package com.example.orders.application;

import com.example.orders.domain.Order;
import com.example.orders.domain.OrderStatus;
import com.example.orders.domain.exceptions.OrderNotFoundException;
import com.example.orders.domain.exceptions.OrderNotPayableException;
import com.example.orders.domain.exceptions.PaymentDeclinedException;
import com.example.orders.domain.exceptions.PaymentServiceException;
import com.example.orders.domain.ports.OrderRepository;
import com.example.orders.domain.ports.PaymentGateway;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.Objects;

/**
 * Application service for order payment processing.
 *
 * <p>Orchestrates the payment flow: validates order state, charges the payment
 * gateway, and persists the updated status. All dependencies are injected via
 * constructor — no global state or service locator.
 *
 * <p>This class follows Clean Architecture: it depends only on interfaces
 * defined in the domain layer, not on infrastructure implementations.
 */
@Service
public class OrderPaymentService {

  private static final Logger log = LoggerFactory.getLogger(OrderPaymentService.class);

  private final OrderRepository orderRepository;
  private final PaymentGateway paymentGateway;

  // ✅ Constructor injection — immutable, testable, explicit dependencies
  public OrderPaymentService(OrderRepository orderRepository, PaymentGateway paymentGateway) {
    this.orderRepository = Objects.requireNonNull(orderRepository, "orderRepository must not be null");
    this.paymentGateway = Objects.requireNonNull(paymentGateway, "paymentGateway must not be null");
  }

  /**
   * Process a payment for an existing pending order.
   *
   * <p>Validates the order is in {@link OrderStatus#PENDING} status, charges the
   * payment gateway, and transitions the order to {@link OrderStatus#PAID}.
   *
   * @param orderId   the ID of the order to process; must not be null or blank
   * @param cardToken tokenized card from the payment provider; must not be null or blank
   * @return the payment confirmation ID
   * @throws OrderNotFoundException   if no order with orderId exists
   * @throws OrderNotPayableException if the order is not in PENDING status
   * @throws PaymentDeclinedException if the payment gateway declines the charge
   * @throws PaymentServiceException  if the payment gateway is unreachable
   */
  @Transactional
  public String processPayment(String orderId, String cardToken) {
    // ✅ Guard clauses — fail fast with clear error messages
    validateArguments(orderId, cardToken);

    Order order = orderRepository.findById(orderId)
        .orElseThrow(() -> new OrderNotFoundException(orderId));

    if (order.getStatus() != OrderStatus.PENDING) {
      throw new OrderNotPayableException(orderId, order.getStatus());
    }

    log.info("Processing payment for order {} amount={} currency={}",
        orderId, order.getTotal(), order.getCurrency());

    String paymentId = chargeGateway(orderId, order, cardToken);

    // ✅ Only update status after payment succeeds
    order.markAsPaid(paymentId);
    orderRepository.save(order);

    log.info("Payment processed successfully orderId={} paymentId={}", orderId, paymentId);
    return paymentId;
  }

  // ✅ Private helper — Single Responsibility: charge + translate errors
  private String chargeGateway(String orderId, Order order, String cardToken) {
    try {
      return paymentGateway.charge(order.getTotal(), order.getCurrency(), cardToken);
    } catch (PaymentDeclinedException e) {
      log.info("Payment declined for order {}: {}", orderId, e.getDeclineCode());
      throw e; // re-throw domain exception as-is
    } catch (Exception e) {
      log.error("Payment gateway error for order {}", orderId, e);
      throw new PaymentServiceException("Payment service temporarily unavailable", e);
    }
  }

  // ✅ Validation extracted to named method for readability
  private void validateArguments(String orderId, String cardToken) {
    if (orderId == null || orderId.isBlank()) {
      throw new IllegalArgumentException("orderId must not be null or blank");
    }
    if (cardToken == null || cardToken.isBlank()) {
      throw new IllegalArgumentException("cardToken must not be null or blank");
    }
  }
}
