# Testing AI Rules

> Full reference: `universal/testing-strategy.md`

---

## Test Pyramid

```
10% E2E       — critical user journeys only
20% Integration — component boundaries, real DB
70% Unit      — fast, isolated, many
```

## Unit Test Rules

- Pattern: **AAA** (Arrange-Act-Assert) — blank line between sections
- Naming: `<method>_<scenario>_<expected_behavior>`
- One logical assertion per test
- FIRST: Fast, Isolated, Repeatable, Self-validating, Timely
- No shared mutable state between tests

```python
# ✅ AAA + naming pattern
def test_charge_card_when_expired_raises_payment_error():
    # Arrange
    expired_card = CardFactory.build(expired=True)
    service = PaymentService(gateway=MockGateway())

    # Act / Assert
    with pytest.raises(PaymentError):
        service.charge(expired_card, amount=Decimal("100.00"))
```

## Coverage Targets

| Code | Minimum |
|------|---------|
| Business logic | 80% line coverage |
| Critical paths (auth, payments) | 100% line + branch |
| Infrastructure adapters | 60% |
| Generated/migrations code | Exempt |

## Corner Case Checklist

Every test suite must cover:
- `null`/`nil`/`None` inputs
- Empty collections
- Boundary values (0, 1, max, min, -1)
- Invalid/malformed inputs
- Unicode/non-ASCII data
- Concurrent execution (if applicable)
- Network failure / timeout

## Mocking Rules

- **Mock at the boundary** (databases, HTTP, queues) — not internal collaborators
- Max 3 mocked dependencies per test — more = design smell
- Prefer **fakes** (lightweight implementations) over mocks where possible
- Don't mock what you don't own (don't mock third-party libs)

## What NOT to Test

- Private implementation details
- Framework/library code
- Trivial getters/setters
- Auto-generated code
- `main()` entry points (covered by E2E)
