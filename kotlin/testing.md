# Kotlin Testing Standards

> **Tools:** JUnit 5, MockK, Kotest, Turbine (Flow testing)

---

## JUnit 5 + MockK

```kotlin
@ExtendWith(MockKExtension::class)
class GetOrdersUseCaseTest {

    @MockK lateinit var orderRepository: OrderRepository
    private lateinit var useCase: GetOrdersUseCase

    @BeforeEach
    fun setUp() {
        useCase = GetOrdersUseCase(orderRepository)
    }

    @Test
    fun `execute returns orders for valid user`() = runTest {
        // Arrange
        val orders = listOf(OrderFactory.pending(), OrderFactory.paid())
        coEvery { orderRepository.findByUserId("user-1") } returns orders

        // Act
        val result = useCase.execute("user-1")

        // Assert
        assertThat(result).isEqualTo(orders)
        coVerify(exactly = 1) { orderRepository.findByUserId("user-1") }
    }

    @Test
    fun `execute throws OrderNotFoundException when user has no orders`() = runTest {
        coEvery { orderRepository.findByUserId("nonexistent") } returns emptyList()

        assertThrows<NoOrdersFoundException> {
            useCase.execute("nonexistent")
        }
    }
}
```

## Flow Testing with Turbine

```kotlin
@Test
fun `watchOrderStatus emits statuses until terminal state`() = runTest {
    val orderService = FakeOrderService()

    orderService.watchOrderStatus("order-1").test {
        assertThat(awaitItem()).isEqualTo(OrderStatus.PENDING)
        assertThat(awaitItem()).isEqualTo(OrderStatus.PROCESSING)
        assertThat(awaitItem()).isEqualTo(OrderStatus.PAID)
        awaitComplete()
    }
}
```

## Test Naming with Backtick Strings

```kotlin
// Kotlin allows spaces in backtick function names — use them in tests
@Test
fun `calculateTotal with empty items returns zero`() { }

@Test
fun `processPayment with declined card throws PaymentDeclinedException`() { }

@Test
fun `findOrder when not found throws OrderNotFoundException`() { }
```
