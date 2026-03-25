# Kotlin Style Guide

> **Sources:** Kotlin Coding Conventions (kotlinlang.org/docs/coding-conventions.html), Android Kotlin Style Guide (developer.android.com/kotlin/style-guide), JetBrains Kotlin team guidance

---

## A. Formatting & Style

### Line Length

**120 characters** (Kotlin Coding Conventions). ktlint enforces this.

> The Android Kotlin Style Guide recommends 100 characters. Kotlin official convention recommends 120. We use 120 for Kotlin backend; use 100 if your project is Android-focused to match Android conventions.

### Indentation

**4 spaces** per level (Kotlin Coding Conventions). Never tabs.

### Trailing Commas (Kotlin 1.4+)

```kotlin
// ✅ Recommended in Kotlin 1.4+
val config = Config(
    host = "localhost",
    port = 5432,
    maxConnections = 10,  // trailing comma
)
```

---

## B. Naming Conventions

| Concept | Convention | Example |
|---------|-----------|---------|
| Classes, interfaces, objects | `PascalCase` | `OrderService`, `PaymentGateway` |
| Functions, properties | `camelCase` | `processPayment`, `isActive` |
| Constants (companion object) | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_CURRENCY` |
| Packages | `lowercase` | `com.company.orders.domain` |
| Boolean properties | `is`, `has`, `can`, `should` | `isActive`, `hasSubscription` |
| Test functions | backtick names (readable) | `` `process payment returns confirmation when card is valid` `` |

---

## C. Kotlin Idioms

### Data Classes for Value Objects

```kotlin
// ✅ GOOD: data class with validation in init
data class Money(val amount: BigDecimal, val currency: String) {
    init {
        require(amount >= BigDecimal.ZERO) { "Amount must be non-negative, got: $amount" }
        require(currency.length == 3) { "Currency must be ISO 4217 (3 chars), got: $currency" }
    }

    operator fun plus(other: Money): Money {
        require(this.currency == other.currency) { "Currency mismatch: $currency vs ${other.currency}" }
        return Money(this.amount + other.amount, this.currency)
    }
}
```

### Sealed Classes for Error Hierarchies

```kotlin
// ✅ GOOD: sealed class for exhaustive when expressions
sealed class PaymentResult {
    data class Success(val paymentId: String, val amount: BigDecimal) : PaymentResult()
    data class Declined(val code: String, val message: String) : PaymentResult()
    data class Error(val cause: Throwable) : PaymentResult()
}

fun handleResult(result: PaymentResult): Response = when (result) {
    is PaymentResult.Success -> Response.ok(result.paymentId)
    is PaymentResult.Declined -> Response.badRequest("Declined: ${result.message}")
    is PaymentResult.Error -> Response.serverError("Service unavailable")
    // ✅ No else needed — sealed class is exhaustive
}
```

### Avoid `!!` Non-null Assertion

```kotlin
// ❌ BAD: crashes with NullPointerException if null
val name = user!!.name

// ✅ GOOD: safe call + Elvis operator
val name = user?.name ?: "Unknown"

// ✅ GOOD: require with descriptive message
val user = userRepo.findById(userId)
    ?: throw OrderNotFoundException("User $userId not found")
```

### Extension Functions for Readability

```kotlin
// ✅ GOOD: extension function on domain type
fun Order.isPayable(): Boolean = this.status == OrderStatus.PENDING

fun BigDecimal.toMoney(currency: String): Money = Money(this, currency)

// Usage
if (order.isPayable()) {
    processPayment(order)
}
```

---

## D. Error Handling

```kotlin
// ✅ GOOD: sealed Result type (Kotlin stdlib)
suspend fun findOrder(id: String): Result<Order> = runCatching {
    orderRepo.findById(id) ?: throw OrderNotFoundException(id)
}

// Caller
val result = findOrder(orderId)
result
    .onSuccess { order -> processPayment(order) }
    .onFailure { error ->
        logger.error("Failed to find order $orderId", error)
        throw PaymentException("Order not found", error)
    }
```

---

## E. Functions

### Prefer Expressions for Simple Functions

```kotlin
// ✅ GOOD: expression body for simple functions
fun calculateTotal(items: List<OrderItem>): BigDecimal =
    items.sumOf { it.unitPrice * it.quantity.toBigDecimal() }

// ✅ GOOD: when as expression
fun statusMessage(status: OrderStatus): String = when (status) {
    OrderStatus.PENDING -> "Awaiting payment"
    OrderStatus.PAID -> "Order confirmed"
    OrderStatus.CANCELLED -> "Order cancelled"
}
```

### Default Parameters Over Overloads

```kotlin
// ✅ GOOD: default parameters
suspend fun findOrders(
    userId: String,
    status: OrderStatus? = null,
    limit: Int = 20,
    offset: Int = 0,
): List<Order>

// Callers:
findOrders("user-1")                              // all orders, limit 20
findOrders("user-1", status = OrderStatus.PAID)  // paid only
findOrders("user-1", limit = 100)                // first 100
```

---

## F. Security

```kotlin
// ❌ BAD: hardcoded credentials
val dbPassword = "super_secret_password"

// ✅ GOOD: from environment
val dbPassword = System.getenv("DB_PASSWORD")
    ?: error("DB_PASSWORD environment variable must be set")

// SQL injection prevention with exposed or JDBI
// ❌ BAD: string interpolation in SQL
val query = "SELECT * FROM users WHERE email = '$email'"

// ✅ GOOD: parameterized (Kotlin Exposed)
Users.select { Users.email eq email }
```
