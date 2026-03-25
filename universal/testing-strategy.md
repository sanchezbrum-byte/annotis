# Testing Strategy

> **Source:** Google Test Engineering practices, Netflix Testing Culture, Martin Fowler's Test Pyramid, FIRST properties (Robert C. Martin), xUnit Patterns (Meszaros)

---

## 1. The Test Pyramid

The test pyramid describes the optimal distribution of tests by layer. Google's internal recommendation:

```
          /‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
         /   E2E / UI      \   ~10% — slow, brittle, expensive
        /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
       /   Integration       \  ~20% — test component boundaries
      /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
     /       Unit              \ ~70% — fast, isolated, many
    /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
```

**Rationale:** Unit tests are cheap to write and run in milliseconds. E2E tests are expensive to maintain and run in minutes. Inverting this pyramid (the "ice cream cone" anti-pattern) leads to slow CI, flaky tests, and poor developer experience.

---

## 2. Unit Test Rules

### FIRST Properties

Every unit test must satisfy all five properties:

| Property | Meaning |
|----------|---------|
| **F**ast | Runs in < 100ms; the entire unit suite in < 30 seconds |
| **I**solated | No shared state between tests; any test can run alone |
| **R**epeatable | Same result every run, regardless of environment or order |
| **S**elf-validating | Pass or fail without manual inspection — no print-and-check |
| **T**imely | Written before or alongside the code (TDD or at worst same PR) |

### AAA Pattern (Arrange-Act-Assert)

Every test must follow this structure:

```python
def test_calculate_order_total_with_discount_returns_discounted_price():
    # Arrange
    order = Order(items=[Item(price=100.00), Item(price=50.00)])
    discount = PercentageDiscount(rate=0.10)

    # Act
    total = calculate_order_total(order, discount)

    # Assert
    assert total == Decimal("135.00")
```

- One blank line between each section
- One logical assertion per test (may have multiple `assert` statements if they test the same behavior)
- Never put business logic in the Arrange section — use factories/builders

### Test Naming Convention

```
<method_or_function>_<scenario>_<expected_behavior>
```

| Language | Format | Example |
|----------|--------|---------|
| Python | `test_<method>_<scenario>_<expected>` | `test_charge_with_expired_card_raises_payment_error` |
| Java/Kotlin | `<method>_<scenario>_<expected>` | `charge_withExpiredCard_throwsPaymentException` |
| JavaScript/TypeScript | `<method> <scenario> <expected>` (describe/it) | `describe('charge') → it('throws when card is expired')` |
| Go | `Test<Method>_<Scenario>` | `TestCharge_ExpiredCard_ReturnsError` |
| Rust | `<method>_<scenario>_<expected>` | `charge_expired_card_returns_err` |

---

## 3. Coverage Targets

| Code Type | Minimum Coverage | Rationale |
|-----------|-----------------|-----------|
| Business logic / domain | **80% line coverage** | Core value; bugs here are costly |
| Critical paths (payments, auth, data integrity) | **100% line + branch coverage** | Zero tolerance for untested paths |
| Adapter/infrastructure code | **60% line coverage** | Harder to unit test; integration tests cover the rest |
| Generated code | **Exempt** | Auto-generated files (migrations, protobuf, etc.) |
| `main()` / entry points | **Exempt from unit** | Covered by integration/E2E tests |

> Coverage is a floor, not a ceiling. 100% coverage does not mean zero bugs. Tests must assert meaningful behavior, not just execute lines.

---

## 4. What NOT to Test

Never write tests for:

1. **Private/internal implementation details** — test public behavior; if you refactor internals, tests should not break
2. **Framework/library code** — don't test that `express` can parse JSON; trust the framework
3. **Trivial getters/setters** — `getName()` returning `this.name` needs no test
4. **Configuration values** — test that configuration is used correctly, not that it exists
5. **Third-party APIs** — mock them; test your adapter layer, not their service

---

## 5. Mocking Rules

### Mock at the Boundary

Mock external systems (databases, HTTP clients, message queues, clocks) — not internal collaborators.

```python
# ✅ GOOD: Mock the external database dependency
def test_get_user_returns_user_when_found(mock_user_repo):
    mock_user_repo.find_by_id.return_value = User(id=1, name="Alice")
    service = UserService(repo=mock_user_repo)
    user = service.get_user(1)
    assert user.name == "Alice"

# ❌ BAD: Mocking internal collaborators tests nothing real
def test_process_order_calls_internal_validator(mock_validator):
    # This test will break on every refactor and tests nothing useful
    mock_validator.validate.return_value = True
    service = OrderService(validator=mock_validator)
    service.process(order)
    mock_validator.validate.assert_called_once()
```

### Over-Mocking Anti-Pattern

If your test requires mocking more than 3 dependencies, the code under test has too many dependencies. Refactor first.

### Types of Test Doubles

| Type | Use | Behavior |
|------|-----|---------|
| **Stub** | Provide canned responses | Returns a fixed value; no assertions |
| **Mock** | Verify interactions | Has expectations on method calls |
| **Spy** | Observe real calls | Wraps real object; records calls |
| **Fake** | Lightweight implementation | In-memory DB, fake clock |
| **Dummy** | Fill parameter slots | Never actually called |

Prefer **fakes** over mocks where possible — they are more realistic and less fragile.

---

## 6. Corner Case Checklist

Before marking any test suite complete, verify coverage for:

- [ ] `null` / `nil` / `None` / `undefined` inputs
- [ ] Empty collections (`[]`, `{}`, `""`)
- [ ] Single-element collections (`[x]`)
- [ ] Boundary values: `0`, `1`, `max_int`, `min_int`, `-1`
- [ ] Very large inputs (stress test — what happens at 10M records?)
- [ ] Negative numbers where only positives are expected
- [ ] Unicode and non-ASCII characters (emojis, RTL text, multi-byte sequences)
- [ ] Whitespace-only strings (`"   "`)
- [ ] Very long strings (beyond typical limits)
- [ ] Concurrent/parallel execution (if applicable)
- [ ] Network failure / timeout scenarios (for I/O-bound code)
- [ ] Partial failures in multi-step operations
- [ ] Idempotency (calling the same operation twice has same result)
- [ ] Out-of-order event delivery (for event-driven systems)

---

## 7. Integration Test Rules

Integration tests verify that components work together correctly at their boundaries.

**Principles:**
1. Use **real databases** when possible — use TestContainers (Java, Go, Python) or Docker Compose for local/CI
2. Use **real message brokers** for event-driven systems — do not mock Kafka in integration tests
3. Test the **HTTP contract** for APIs — real HTTP client against real server process
4. Isolate each test by resetting state — use transactions rolled back after each test, or truncate tables
5. Keep integration tests **deterministic** — avoid time-dependent behavior; inject a fake clock

**TestContainers Example:**
```python
# pytest + testcontainers-python
@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as pg:
        yield pg

def test_user_repository_saves_and_retrieves_user(postgres_container):
    repo = UserRepository(db_url=postgres_container.get_connection_url())
    user = User(name="Alice", email="alice@example.com")
    repo.save(user)
    retrieved = repo.find_by_email("alice@example.com")
    assert retrieved.name == "Alice"
```

---

## 8. E2E Test Rules

E2E tests validate full user journeys through the deployed system.

**Principles:**
1. Test only **critical user journeys** — not every feature permutation
2. Keep E2E count small (< 50 total for most applications)
3. Use **real environments** — staging or a dedicated test environment
4. Make tests **independent** — each test creates its own data, never depends on other tests
5. Build in **retry logic** for inherently flaky operations (network, timing)
6. E2E tests should **not replace** unit tests for edge cases

**High-value E2E test candidates:**
- User registration and login
- Core purchase/checkout flow
- Data export/import
- Password reset
- Critical admin operations

---

## 9. Test Data Management

### Factories Over Magic Numbers

```python
# ❌ BAD: Magic numbers, unclear what's being tested
def test_order_discount():
    order = Order(user_id=1, items=[{"id": 5, "price": 100}], status="pending")
    assert apply_discount(order, 0.1) == 90

# ✅ GOOD: Named factories, explicit intent
def test_order_discount_applies_correctly_to_eligible_order():
    order = OrderFactory.build(
        status=OrderStatus.PENDING,
        items=[ItemFactory.build(price=Decimal("100.00"))],
    )
    discount = DiscountFactory.build(rate=Decimal("0.10"))
    assert apply_discount(order, discount) == Decimal("90.00")
```

### Rules for Test Data
- Use **factories** (factory_boy, FactoryBot, GoFakeIt) not hardcoded fixtures for unit/integration tests
- Use **fixed seed data** (SQL fixtures or migration seeds) for E2E tests that need stable state
- Never use production data in tests — it violates privacy and creates data dependency
- Make test data **self-describing** — variable names explain what the data represents

---

## 10. Continuous Integration Requirements

Every CI pipeline must run, in order:

1. **Linting / static analysis** (fastest; fail fast on style errors)
2. **Unit tests** (< 2 minutes total; fail fast)
3. **Integration tests** (< 10 minutes total)
4. **Security scanning** (SAST: semgrep, bandit, gosec)
5. **Coverage report** (fail if below threshold)
6. **E2E tests** (triggered on merge to `main` or release branch only)

**Golden rule:** If CI is red, fixing it is the team's #1 priority. No one merges until the trunk is green.
