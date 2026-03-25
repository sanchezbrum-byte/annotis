# Java Architecture

## Spring Boot Clean Architecture

See `universal/architecture.md` for full Clean Architecture description. The Java/Spring Boot–specific implementation follows the structure in `style-guide.md`.

## Key Spring Boot Conventions

### Application Properties

```yaml
# application.yml — use YAML, not .properties
spring:
  application:
    name: order-service
  datasource:
    url: ${DATABASE_URL}          # Always from environment
    username: ${DATABASE_USER}
    password: ${DATABASE_PASSWORD}
  jpa:
    open-in-view: false           # Always disable — prevents lazy loading across HTTP request
    hibernate:
      ddl-auto: validate          # Never `create` or `update` in production
  flyway:
    enabled: true
    locations: classpath:db/migration

# Never put secrets in application.yml — use env vars or Vault
```

### Configuration as Code

```java
// ✅ Typed configuration with validation
@ConfigurationProperties(prefix = "payment")
@Validated
public record PaymentConfig(
  @NotBlank String gatewayUrl,
  @NotBlank String apiKey,
  @Positive int timeoutSeconds,
  @Min(1) @Max(5) int maxRetries
) {}
```

## Testing Conventions

```java
// Unit test (no Spring context)
@ExtendWith(MockitoExtension.class)
class SubmitOrderUseCaseTest {
  @Mock OrderRepository orderRepository;
  @Mock PaymentGateway paymentGateway;
  @InjectMocks SubmitOrderUseCase useCase;

  @Test
  void execute_withValidRequest_returnsConfirmation() {
    // Arrange
    Order pendingOrder = OrderFixture.pendingOrder();
    given(orderRepository.findById(pendingOrder.getId()))
      .willReturn(Optional.of(pendingOrder));
    given(paymentGateway.charge(any(), any()))
      .willReturn(PaymentFixture.successfulPayment());

    // Act
    var result = useCase.execute(new SubmitOrderRequest(pendingOrder.getId(), "tok_visa"));

    // Assert
    assertThat(result.status()).isEqualTo(OrderStatus.PAID);
    verify(orderRepository).save(pendingOrder);
  }
}

// Integration test (full Spring context with Testcontainers)
@SpringBootTest
@Testcontainers
class OrderRepositoryIT {
  @Container
  static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");

  @DynamicPropertySource
  static void configureProperties(DynamicPropertyRegistry registry) {
    registry.add("spring.datasource.url", postgres::getJdbcUrl);
    registry.add("spring.datasource.username", postgres::getUsername);
    registry.add("spring.datasource.password", postgres::getPassword);
  }
}
```
