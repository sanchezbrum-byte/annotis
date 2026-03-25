package com.example.orders.application

import com.example.orders.domain.Order
import com.example.orders.domain.OrderStatus
import io.mockk.*
import io.mockk.impl.annotations.MockK
import kotlinx.coroutines.test.runTest
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.*
import java.math.BigDecimal
import java.time.Instant

/**
 * Unit tests for [OrderPaymentService].
 *
 * Uses MockK for suspending function mocks and kotlinx-coroutines-test for
 * structured coroutine testing (runTest).
 *
 * Each test follows Arrange → Act → Assert.
 */
@DisplayName("OrderPaymentService")
class OrderPaymentServiceTest {

    @MockK lateinit var orderRepository: OrderRepository
    @MockK lateinit var paymentGateway: PaymentGateway

    private lateinit var service: OrderPaymentService

    @BeforeEach
    fun setUp() {
        MockKAnnotations.init(this)
        service = OrderPaymentService(orderRepository, paymentGateway)
    }

    // -------------------------------------------------------------------------
    // Test helpers
    // -------------------------------------------------------------------------

    private fun buildPendingOrder(orderId: String = "order-123") = Order(
        id = orderId,
        userId = "user-456",
        total = Money(BigDecimal("100.00"), "USD"),
        status = OrderStatus.PENDING,
        createdAt = Instant.now(),
    )

    // -------------------------------------------------------------------------
    // Happy path
    // -------------------------------------------------------------------------

    @Nested
    @DisplayName("Given a valid pending order and a successful payment gateway")
    inner class HappyPath {

        @Test
        @DisplayName("processPayment returns Success with paymentId")
        fun processPayment_validCard_returnsSuccess() = runTest {
            // Arrange
            val order = buildPendingOrder()
            coEvery { orderRepository.findById("order-123") } returns order
            coEvery { paymentGateway.charge(any(), any(), any()) } returns "pay-789"
            coJustRun { orderRepository.save(any()) }

            // Act
            val result = service.processPayment("order-123", "tok_visa")

            // Assert
            assertThat(result).isInstanceOf(PaymentResult.Success::class.java)
            assertThat((result as PaymentResult.Success).paymentId).isEqualTo("pay-789")
            coVerify { orderRepository.save(match { it.status == OrderStatus.PAID }) }
        }
    }

    // -------------------------------------------------------------------------
    // Precondition validation
    // -------------------------------------------------------------------------

    @Nested
    @DisplayName("Input validation")
    inner class Validation {

        @Test
        @DisplayName("blank orderId throws IllegalArgumentException")
        fun processPayment_blankOrderId_throwsIllegalArgument() = runTest {
            assertThrows<IllegalArgumentException> {
                service.processPayment("  ", "tok_visa")
            }
            coVerify(exactly = 0) { orderRepository.findById(any()) }
        }

        @Test
        @DisplayName("blank cardToken throws IllegalArgumentException")
        fun processPayment_blankCardToken_throwsIllegalArgument() = runTest {
            assertThrows<IllegalArgumentException> {
                service.processPayment("order-123", "")
            }
            coVerify(exactly = 0) { orderRepository.findById(any()) }
        }
    }

    // -------------------------------------------------------------------------
    // Order state errors
    // -------------------------------------------------------------------------

    @Nested
    @DisplayName("Order state errors")
    inner class OrderStateErrors {

        @Test
        @DisplayName("not found returns ServiceError")
        fun processPayment_orderNotFound_returnsServiceError() = runTest {
            coEvery { orderRepository.findById("missing") } returns null

            val result = service.processPayment("missing", "tok_visa")

            assertThat(result).isInstanceOf(PaymentResult.ServiceError::class.java)
            coVerify(exactly = 0) { paymentGateway.charge(any(), any(), any()) }
        }

        @Test
        @DisplayName("already-paid order returns ServiceError without charging")
        fun processPayment_alreadyPaid_returnsServiceError() = runTest {
            val order = buildPendingOrder().copy(status = OrderStatus.PAID)
            coEvery { orderRepository.findById(order.id) } returns order

            val result = service.processPayment(order.id, "tok_visa")

            assertThat(result).isInstanceOf(PaymentResult.ServiceError::class.java)
            coVerify(exactly = 0) { paymentGateway.charge(any(), any(), any()) }
        }
    }

    // -------------------------------------------------------------------------
    // Gateway failures — verify data integrity (no save on failure)
    // -------------------------------------------------------------------------

    @Nested
    @DisplayName("Gateway failures")
    inner class GatewayFailures {

        @Test
        @DisplayName("declined payment returns Declined without saving order")
        fun processPayment_cardDeclined_returnsDeclined() = runTest {
            val order = buildPendingOrder()
            coEvery { orderRepository.findById(order.id) } returns order
            coEvery { paymentGateway.charge(any(), any(), any()) } throws
                PaymentDeclinedException("insufficient_funds", "Card declined")

            val result = service.processPayment(order.id, "tok_declined")

            assertThat(result).isInstanceOf(PaymentResult.Declined::class.java)
            // ✅ Data integrity: order must NOT be saved after failure
            coVerify(exactly = 0) { orderRepository.save(any()) }
        }

        @Test
        @DisplayName("gateway exception returns ServiceError")
        fun processPayment_gatewayUnavailable_returnsServiceError() = runTest {
            val order = buildPendingOrder()
            coEvery { orderRepository.findById(order.id) } returns order
            coEvery { paymentGateway.charge(any(), any(), any()) } throws
                RuntimeException("connection refused")

            val result = service.processPayment(order.id, "tok_visa")

            assertThat(result).isInstanceOf(PaymentResult.ServiceError::class.java)
            coVerify(exactly = 0) { orderRepository.save(any()) }
        }
    }
}
