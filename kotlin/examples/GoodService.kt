package com.example.orders.application

import com.example.orders.domain.*
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.async
import org.slf4j.LoggerFactory
import java.math.BigDecimal

// ✅ Data class for immutable value objects with validation
data class Money(val amount: BigDecimal, val currency: String) {
    init {
        require(amount >= BigDecimal.ZERO) { "Amount must be non-negative, got: $amount" }
        require(currency.length == 3) { "Currency must be ISO 4217 (3 chars), got: $currency" }
    }

    operator fun plus(other: Money): Money {
        require(currency == other.currency) { "Currency mismatch: $currency vs ${other.currency}" }
        return Money(amount + other.amount, currency)
    }
}

// ✅ Sealed class for exhaustive handling — no else needed in when expressions
sealed class PaymentResult {
    data class Success(val paymentId: String, val amount: BigDecimal) : PaymentResult()
    data class Declined(val code: String, val message: String) : PaymentResult()
    data class ServiceError(val message: String, val cause: Throwable? = null) : PaymentResult()
}

// ✅ Interface for dependency injection — accept interfaces, return concrete types
interface OrderRepository {
    suspend fun findById(orderId: String): Order?
    suspend fun save(order: Order)
}

interface PaymentGateway {
    suspend fun charge(amount: BigDecimal, currency: String, cardToken: String): String
}

// ✅ Service uses constructor injection
class OrderPaymentService(
    private val orderRepository: OrderRepository,
    private val paymentGateway: PaymentGateway,
) {
    private val logger = LoggerFactory.getLogger(OrderPaymentService::class.java)

    /**
     * Process a payment for an existing pending order.
     *
     * @param orderId The ID of the order to process. Must not be blank.
     * @param cardToken Tokenized card from the payment provider.
     * @return [PaymentResult] describing the outcome.
     */
    suspend fun processPayment(orderId: String, cardToken: String): PaymentResult {
        // ✅ require() for precondition validation
        require(orderId.isNotBlank()) { "orderId must not be blank" }
        require(cardToken.isNotBlank()) { "cardToken must not be blank" }

        val order = orderRepository.findById(orderId)
            ?: return PaymentResult.ServiceError("Order $orderId not found")

        if (order.status != OrderStatus.PENDING) {
            return PaymentResult.ServiceError(
                "Order $orderId is not payable (status: ${order.status})"
            )
        }

        logger.info("Processing payment for order $orderId, amount ${order.total}")

        return try {
            val paymentId = paymentGateway.charge(order.total.amount, order.total.currency, cardToken)
            order.status = OrderStatus.PAID
            orderRepository.save(order)

            logger.info("Payment processed: paymentId=$paymentId, orderId=$orderId")
            PaymentResult.Success(paymentId, order.total.amount)
        } catch (e: PaymentDeclinedException) {
            logger.info("Payment declined for order $orderId: ${e.code}")
            PaymentResult.Declined(e.code, e.message ?: "Card declined")
        } catch (e: Exception) {
            logger.error("Payment gateway error for order $orderId", e)
            PaymentResult.ServiceError("Payment service unavailable", e)
        }
    }
}

// ✅ Extension function for concise domain logic
fun PaymentResult.isSuccessful(): Boolean = this is PaymentResult.Success

// ✅ Structured concurrency: parallel data loading
class DashboardService(
    private val orderRepository: OrderRepository,
    private val userService: UserService,
    private val notificationService: NotificationService,
) {
    suspend fun loadDashboard(userId: String): Dashboard = coroutineScope {
        // ✅ async for parallel independent operations
        val ordersDeferred = async { orderRepository.findByUserId(userId) }
        val userDeferred = async { userService.findById(userId) }
        val notificationsDeferred = async { notificationService.getUnread(userId) }

        Dashboard(
            user = userDeferred.await(),
            orders = ordersDeferred.await(),
            notifications = notificationsDeferred.await(),
        )
    }
}
