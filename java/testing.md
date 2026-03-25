# Java Testing Standards

> **Tools:** JUnit 5, Mockito, AssertJ, Testcontainers, Spring Boot Test

---

## Test Naming (JUnit 5)

```java
@Test
void methodName_scenario_expectedBehavior() { }

// Examples:
void processPayment_withValidCard_returnsConfirmation() { }
void processPayment_withDeclinedCard_throwsPaymentDeclinedException() { }
void findOrder_whenNotFound_returnsEmptyOptional() { }
void calculateTotal_withEmptyItems_throwsIllegalArgumentException() { }
```

## AAA Pattern

```java
@Test
void createOrder_withValidItems_persistsAndReturnsOrder() {
  // Arrange
  var request = CreateOrderRequest.builder()
    .userId("user-1")
    .items(List.of(new OrderItem("prod-1", 2, new BigDecimal("25.00"))))
    .currency("USD")
    .build();
  var expectedOrder = OrderFixture.pendingOrder();
  given(orderRepository.save(any(Order.class))).willReturn(expectedOrder);

  // Act
  var result = useCase.execute(request);

  // Assert — use AssertJ for fluent, readable assertions
  assertThat(result).isNotNull();
  assertThat(result.getStatus()).isEqualTo(OrderStatus.PENDING);
  assertThat(result.getUserId()).isEqualTo("user-1");
  verify(orderRepository, times(1)).save(any(Order.class));
}
```

## Parameterized Tests

```java
@ParameterizedTest(name = "{index}: {0} → should throw ValidationException")
@MethodSource("invalidOrderRequests")
void createOrder_withInvalidInput_throwsValidationException(CreateOrderRequest request) {
  assertThatThrownBy(() -> useCase.execute(request))
    .isInstanceOf(ValidationException.class);
}

static Stream<Arguments> invalidOrderRequests() {
  return Stream.of(
    Arguments.of(CreateOrderRequest.builder().userId(null).build()),
    Arguments.of(CreateOrderRequest.builder().userId("").build()),
    Arguments.of(CreateOrderRequest.builder().userId("u1").items(emptyList()).build()),
    Arguments.of(CreateOrderRequest.builder().userId("u1").currency("XYZ").build())
  );
}
```

## Coverage

```xml
<!-- pom.xml -->
<plugin>
  <groupId>org.jacoco</groupId>
  <artifactId>jacoco-maven-plugin</artifactId>
  <configuration>
    <rules>
      <rule>
        <limits>
          <limit>
            <counter>LINE</counter>
            <minimum>0.80</minimum>
          </limit>
        </limits>
      </rule>
    </rules>
  </configuration>
</plugin>
```
