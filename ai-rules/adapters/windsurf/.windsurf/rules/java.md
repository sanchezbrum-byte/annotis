# Java AI Rules

> Full reference: `java/style-guide.md`

---

## Formatting (Google Java Style)

- Column limit: **100 chars**
- Indentation: **2 spaces** (Google Java Style — NOT Oracle's 4 spaces)
- Brace style: K&R (Egyptian)
- No wildcard imports

## Naming

| Concept | Style | Example |
|---------|-------|---------|
| Classes/Interfaces | `PascalCase` | `OrderService`, `PaymentRepository` |
| Methods/Variables | `camelCase` | `processPayment`, `orderId` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Packages | `lowercase.dotted` | `com.company.orders.domain` |
| Test methods | `method_scenario_expected` | `processPayment_withDeclinedCard_throwsException` |

## Functions

- Max **40 lines** per method
- Max **4 parameters** — use Builder for more (Effective Java Item 2)
- Use `Optional<T>` for nullable returns (Effective Java Item 55)
- Use records for immutable data (Java 16+)

```java
// ✅ Optional return
public Optional<User> findByEmail(String email) {
    return Optional.ofNullable(userRepository.findByEmail(email));
}

// ✅ Record for value object
public record Money(BigDecimal amount, Currency currency) {
    public Money { require(amount.compareTo(BigDecimal.ZERO) >= 0, "Amount must be ≥ 0"); }
}
```

## Error Handling

```java
// ✅ Specific exceptions, logged, wrapped
try {
    return paymentGateway.charge(amount, cardToken);
} catch (GatewayDeclineException e) {
    log.info("Payment declined for order {}: {}", orderId, e.getDeclineCode());
    throw new PaymentDeclinedException(e.getDeclineCode());
} catch (GatewayException e) {
    log.error("Gateway error for order {}", orderId, e);
    throw new PaymentServiceException("Service unavailable", e);
}

// ❌ Never
catch (Exception e) { /* silent */ }
```

## Security

```java
// ✅ Parameterized queries
em.createQuery("SELECT u FROM User u WHERE u.email = :email", User.class)
    .setParameter("email", email).getSingleResult();

// ❌ String concatenation in SQL
String q = "SELECT * FROM users WHERE email = '" + email + "'"; // SQLi!

// ✅ Secrets from environment
@Value("${stripe.api-key}") String stripeApiKey; // injected from env
```

## Tooling

```bash
./gradlew spotlessApply  # format (google-java-format)
./gradlew checkstyleMain # lint
./gradlew test           # test
./gradlew dependencyCheckAnalyze  # security scan
```
