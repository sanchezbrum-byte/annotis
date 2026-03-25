# Kotlin AI Rules

> Full reference: `kotlin/style-guide.md`

---

## Formatting (ktlint)

- Line limit: **120 chars** (Kotlin Conventions) / **100 chars** (Android)
- Indentation: **4 spaces**
- Trailing commas: recommended (Kotlin 1.4+)

## Naming

| Concept | Style | Example |
|---------|-------|---------|
| Classes/objects | `PascalCase` | `OrderService` |
| Functions/properties | `camelCase` | `processPayment`, `isActive` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Test functions | backtick names | `` `process payment returns confirmation` `` |
| Boolean | `is/has/can/should` | `isActive`, `hasSubscription` |

## Idioms

```kotlin
// ✅ Data classes for value objects
data class Money(val amount: BigDecimal, val currency: String) {
    init { require(amount >= BigDecimal.ZERO) { "Amount must be ≥ 0" } }
}

// ✅ Sealed classes for exhaustive when
sealed class PaymentResult {
    data class Success(val paymentId: String) : PaymentResult()
    data class Declined(val code: String) : PaymentResult()
    data class Error(val cause: Throwable) : PaymentResult()
}

// ❌ AVOID !! non-null assertion
val name = user!!.name     // crashes — use safe call instead

// ✅ Safe calls + Elvis
val name = user?.name ?: "Unknown"
```

## Coroutines

```kotlin
// ✅ Parallel execution with async
suspend fun getDashboard(userId: String) = coroutineScope {
    val user = async { userService.fetchUser(userId) }
    val orders = async { orderService.fetchOrders(userId) }
    Dashboard(user = user.await(), orders = orders.await())
}

// ✅ StateFlow for UI state
private val _state = MutableStateFlow<State>(State.Loading)
val state = _state.asStateFlow()

// ❌ NEVER GlobalScope — leaks; use viewModelScope / lifecycleScope
GlobalScope.launch { ... }
```

## Error Handling

```kotlin
// ✅ Kotlin Result type
suspend fun findOrder(id: String): Result<Order> = runCatching {
    orderRepo.findById(id) ?: throw OrderNotFoundException(id)
}

// ✅ require/check for invariants
fun createOrder(userId: String, items: List<Item>) {
    require(userId.isNotBlank()) { "userId must not be blank" }
    require(items.isNotEmpty()) { "items must not be empty" }
}
```

## Tooling

```bash
./gradlew ktlintFormat  # format
./gradlew detekt        # lint
./gradlew test          # test
```
