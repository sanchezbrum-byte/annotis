# Kotlin Coroutines

---

## Structured Concurrency

```kotlin
// ✅ GOOD: use coroutineScope for structured concurrency
suspend fun loadDashboard(userId: String): Dashboard = coroutineScope {
    val userDeferred = async { userService.fetchUser(userId) }
    val ordersDeferred = async { orderService.fetchOrders(userId) }
    val notificationsDeferred = async { notificationService.fetchUnread(userId) }

    Dashboard(
        user = userDeferred.await(),
        orders = ordersDeferred.await(),
        notifications = notificationsDeferred.await(),
    )
}
```

## Dispatcher Selection

```kotlin
// IO-bound work (network, disk)
withContext(Dispatchers.IO) {
    orderRepository.findByUserId(userId)
}

// CPU-bound work (heavy computation)
withContext(Dispatchers.Default) {
    computeRecommendations(userHistory)
}

// Main thread (Android UI updates)
withContext(Dispatchers.Main) {
    viewModel.updateUI(result)
}
```

## Flow for Reactive Streams

```kotlin
// ✅ GOOD: Flow for observable streams
fun watchOrderStatus(orderId: String): Flow<OrderStatus> = flow {
    while (true) {
        val status = orderRepo.getStatus(orderId)
        emit(status)
        if (status.isTerminal()) break
        delay(5_000) // poll every 5 seconds
    }
}

// ✅ StateFlow for UI state
class OrderViewModel(private val useCase: GetOrdersUseCase) : ViewModel() {
    private val _state = MutableStateFlow<OrderListState>(OrderListState.Loading)
    val state: StateFlow<OrderListState> = _state.asStateFlow()

    fun loadOrders(userId: String) {
        viewModelScope.launch {
            _state.value = OrderListState.Loading
            _state.value = try {
                val orders = useCase.execute(userId)
                OrderListState.Success(orders)
            } catch (e: Exception) {
                OrderListState.Error(e.message ?: "Unknown error")
            }
        }
    }
}
```

## Never Use GlobalScope

```kotlin
// ❌ BAD: GlobalScope leaks; not tied to lifecycle
GlobalScope.launch {
    processPayment(orderId)
}

// ✅ GOOD: use CoroutineScope tied to lifecycle
class PaymentService(private val scope: CoroutineScope) {
    fun processAsync(orderId: String) {
        scope.launch {
            processPayment(orderId)
        }
    }
}
```
