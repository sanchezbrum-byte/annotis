# Java Style Guide

> **Sources:** Google Java Style Guide (google.github.io/styleguide/javaguide.html), Oracle Code Conventions, "Effective Java" (3rd ed., Joshua Bloch)

---

## A. Formatting & Style

### Line Length

| Limit | Value | Source |
|-------|-------|--------|
| **Column limit** | **100 characters** | Google Java Style Guide §4.4 |

Lines exceeding 100 characters must be line-wrapped at logical breaking points.

### Indentation

- **2 spaces** per level (Google Java Style Guide §4.2)
- **4 spaces** for continuation lines (statements that wrap across lines)
- **Never use tabs** — configure your IDE to insert spaces

> Note: Oracle's legacy recommendation was 4 spaces. Google's guide specifies 2. We follow Google's 2-space rule for consistency.

### Brace Style

Always use braces — K&R (Egyptian) style (Google Java Style Guide §4.1):

```java
// ✅ GOOD: opening brace on same line
public class OrderService {
  public Order createOrder(CreateOrderRequest request) {
    if (request.getItems().isEmpty()) {
      throw new IllegalArgumentException("Items cannot be empty");
    }
    return orderRepository.save(new Order(request));
  }
}

// ❌ BAD: Allman style (brace on next line) — not used in Google style
public class OrderService
{
  public Order createOrder(CreateOrderRequest request)
  {
  }
}
```

### Import Ordering

```java
// 1. Standard library (java.*, javax.*)
import java.util.List;
import java.util.Optional;

// 2. Third-party (blank line separator)
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

// 3. Static imports (blank line separator)
import static org.assertj.core.api.Assertions.assertThat;
```

- No wildcard imports (`import java.util.*`) — Google Java Style Guide §3.3.1

### Blank Lines

- **2 blank lines** between top-level class definitions
- **1 blank line** between methods
- No blank line after class opening brace or before class closing brace

---

## B. Naming Conventions

| Concept | Convention | Example |
|---------|-----------|---------|
| Packages | `lowercase.with.dots` | `com.company.orders.domain` |
| Classes | `PascalCase` | `OrderService`, `PaymentRepository` |
| Interfaces | `PascalCase` (no `I` prefix) | `OrderRepository`, `PaymentGateway` |
| Methods | `camelCase` | `createOrder`, `findByUserId` |
| Variables | `camelCase` | `orderId`, `totalPrice` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRY_ATTEMPTS`, `DEFAULT_CURRENCY` |
| Type params | Single uppercase letter or descriptive | `T`, `E`, `K`, `V`, `TEntity` |
| Test methods | `methodName_scenario_expectedBehavior` | `createOrder_withEmptyItems_throwsException` |

### Boolean Naming

```java
// ✅ GOOD
boolean isActive;
boolean hasPermission;
boolean shouldRetry;

// ❌ BAD
boolean active;
boolean flag;
boolean status;
```

---

## C. Functions & Methods

### Single Responsibility

```java
// ❌ BAD: method does three things
public User registerUser(String email, String password) {
  String hashedPassword = BCrypt.hash(password, 12);
  User user = userRepository.save(new User(email, hashedPassword));
  emailService.sendWelcomeEmail(user.getEmail()); // side effect mixed in
  metricsService.increment("user.registered");    // second side effect
  return user;
}

// ✅ GOOD: each concern is separated
public User registerUser(String email, String password) {
  String hashedPassword = passwordEncoder.encode(password);
  return userRepository.save(new User(email, hashedPassword));
}
// Caller (or orchestrating use case) calls sendWelcomeEmail separately
```

### Maximum Parameters — Use Builder for > 4

```java
// ❌ BAD: 7 parameters
public Order createOrder(String userId, List<Item> items, String currency,
  String discountCode, Address shippingAddress, PaymentMethod paymentMethod,
  String notes) { }

// ✅ GOOD: builder pattern (Effective Java Item 2)
Order order = Order.builder()
  .userId(userId)
  .items(items)
  .currency(currency)
  .discountCode(discountCode)
  .shippingAddress(shippingAddress)
  .paymentMethod(paymentMethod)
  .build();
```

### Use Optionals for Nullable Returns (Effective Java Item 55)

```java
// ❌ BAD: returning null — callers can forget null check
public User findByEmail(String email) {
  return userRepository.findByEmail(email); // could return null
}

// ✅ GOOD: Optional makes absence explicit
public Optional<User> findByEmail(String email) {
  return Optional.ofNullable(userRepository.findByEmail(email));
}

// Caller:
userService.findByEmail(email)
  .orElseThrow(() -> new UserNotFoundException(email));
```

### Prefer Records for Immutable Data (Java 16+)

```java
// ✅ Immutable value object as a record
public record Money(BigDecimal amount, Currency currency) {
  public Money {
    Objects.requireNonNull(amount, "amount cannot be null");
    Objects.requireNonNull(currency, "currency cannot be null");
    if (amount.compareTo(BigDecimal.ZERO) < 0) {
      throw new IllegalArgumentException("Amount cannot be negative");
    }
  }

  public Money add(Money other) {
    if (!this.currency.equals(other.currency)) {
      throw new CurrencyMismatchException(this.currency, other.currency);
    }
    return new Money(this.amount.add(other.amount), this.currency);
  }
}
```

---

## D. Comments & Documentation

### Javadoc (Required for all public API)

```java
/**
 * Process a payment for an existing order.
 *
 * <p>Validates the order is in PENDING status, charges the payment gateway,
 * and transitions the order to PAID status. Publishes a {@link PaymentProcessedEvent}.
 *
 * @param orderId  the ID of the order to pay; must not be null
 * @param cardToken tokenized card from the payment provider; must not be blank
 * @return the processed payment with a confirmation ID
 * @throws OrderNotFoundException  if no order with the given ID exists
 * @throws OrderNotPayableException if the order is not in PENDING status
 * @throws PaymentDeclinedException if the payment gateway declines the charge
 */
public PaymentConfirmation processPayment(String orderId, String cardToken) { ... }
```

### Inline Comments — WHY Not WHAT

```java
// ✅ GOOD: explains non-obvious intent
// Stripe idempotency window is 24h. Scoping the key by date allows safe
// retry within the same day without risk of double-charge.
String idempotencyKey = orderId + ":" + LocalDate.now();

// ❌ BAD: restates the code
// Get the user by ID
User user = userRepository.findById(userId);
```

---

## E. Error Handling

### Custom Exception Hierarchy

```java
// Domain exception hierarchy
public class AppException extends RuntimeException { ... }

public class DomainException extends AppException {
  public DomainException(String message) { super(message); }
  public DomainException(String message, Throwable cause) { super(message, cause); }
}

public class OrderNotFoundException extends DomainException {
  public OrderNotFoundException(String orderId) {
    super("Order not found: " + orderId);
  }
}
```

### Never Swallow Exceptions

```java
// ❌ BAD: silently swallowed
try {
  result = riskyOperation();
} catch (Exception e) {
  // silent — this is never acceptable
}

// ✅ GOOD: log and translate
try {
  return paymentGateway.charge(amount, cardToken);
} catch (GatewayDeclineException e) {
  log.info("Payment declined for order {}: {}", orderId, e.getDeclineCode());
  throw new PaymentDeclinedException(e.getDeclineCode());
} catch (GatewayException e) {
  log.error("Payment gateway error for order {}", orderId, e);
  throw new PaymentServiceException("Payment service temporarily unavailable", e);
}
```

---

## F. Architecture Rules

### Spring Boot Project Structure

```
src/
  main/
    java/com/company/myapp/
      domain/
        order/
          Order.java
          OrderRepository.java    # Interface
          OrderService.java       # Domain service
        payment/
          ...
      application/
        order/
          SubmitOrderUseCase.java
          SubmitOrderRequest.java
      adapters/
        http/
          order/
            OrderController.java
            OrderRequest.java    # Jackson DTOs
            OrderResponse.java
        persistence/
          order/
            OrderEntity.java     # JPA entity
            JpaOrderRepository.java  # Spring Data
            OrderMapper.java     # Entity ↔ Domain mapping
      shared/
        config/
          SecurityConfig.java
          DatabaseConfig.java
        exception/
          GlobalExceptionHandler.java
    resources/
      application.yml
      db/migration/           # Flyway migrations
  test/
    java/com/company/myapp/
      domain/
      application/
      adapters/
        http/
        persistence/
```

### Layer Rules

- `@Controller` — HTTP only; never business logic
- `@Service` (use case or domain service) — business logic; no HTTP or JPA
- `@Repository` — data access only; no business logic
- No direct JPA `EntityManager` calls in `@Service` — always through repository interface

---

## G. Performance

### Use `BigDecimal` for Money (Effective Java Item 60)

```java
// ❌ BAD: floating-point arithmetic loses precision for money
double price = 1.03 + 0.42; // 1.4499999999999997 — NOT 1.45

// ✅ GOOD: BigDecimal for exact decimal arithmetic
BigDecimal price = new BigDecimal("1.03").add(new BigDecimal("0.42")); // 1.45
```

---

## H. Security

### SQL Injection Prevention

```java
// ❌ BAD: string concatenation in JPQL
String jpql = "SELECT u FROM User u WHERE u.email = '" + email + "'";
List<User> users = em.createQuery(jpql).getResultList();

// ✅ GOOD: named parameter binding
List<User> users = em.createQuery(
  "SELECT u FROM User u WHERE u.email = :email", User.class)
  .setParameter("email", email)
  .getResultList();

// ✅ BEST: Spring Data JPA repository method (auto-parameterized)
Optional<User> user = userRepository.findByEmail(email);
```
