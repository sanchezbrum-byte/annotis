# Python Testing Standards

> **Tools:** pytest, pytest-cov, factory-boy, testcontainers, pytest-asyncio

---

## Test Structure

```
tests/
  conftest.py           # Shared fixtures
  unit/
    domain/
      test_order.py
      test_user.py
    application/
      test_submit_order.py
  integration/
    persistence/
      test_order_repository.py
    http/
      test_orders_api.py
  e2e/
    test_checkout_flow.py
```

## pytest Conventions

### AAA Pattern

```python
def test_apply_discount_with_percentage_discount_reduces_total():
    # Arrange
    order = OrderFactory.build(
        items=[ItemFactory.build(price=Decimal("100.00"))]
    )
    discount = PercentageDiscount(rate=Decimal("0.10"))

    # Act
    result = apply_discount(order, discount)

    # Assert
    assert result.total == Decimal("90.00")
```

### Fixtures

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as pg:
        yield pg

@pytest.fixture(scope="session")
def db_engine(postgres_container):
    engine = create_engine(postgres_container.get_connection_url())
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()  # Roll back after each test for isolation
    connection.close()
```

### Parametrize for Multiple Cases

```python
import pytest
from decimal import Decimal

@pytest.mark.parametrize("amount,currency,expected_error", [
    (Decimal("-1.00"), "USD", "Amount must be positive"),
    (Decimal("0.00"),  "USD", "Amount must be positive"),
    (Decimal("10.00"), "XYZ", "Unsupported currency: XYZ"),
    (None,             "USD", "Amount is required"),
])
def test_create_order_with_invalid_input_raises_validation_error(
    amount, currency, expected_error
):
    with pytest.raises(ValidationError, match=expected_error):
        CreateOrderRequest(user_id="u1", amount=amount, currency=currency)
```

### Mocking Best Practices

```python
from unittest.mock import AsyncMock, MagicMock, patch

def test_submit_order_publishes_event_on_success(mock_event_bus):
    # Use constructor injection, not global mocking
    order_repo = FakeOrderRepository()
    user_repo = FakeUserRepository()
    event_bus = MagicMock()

    use_case = SubmitOrderUseCase(
        order_repo=order_repo,
        user_repo=user_repo,
        event_bus=event_bus,
    )
    order = OrderFactory.build(status=OrderStatus.PENDING)
    order_repo.save(order)

    use_case.execute(order_id=order.id, user_id="u1")

    event_bus.publish.assert_called_once_with(
        OrderSubmittedEvent(order_id=order.id)
    )
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_fetch_user_returns_user_when_found():
    repo = AsyncFakeUserRepository()
    await repo.save(UserFactory.build(id="u1", name="Alice"))

    result = await repo.find_by_id("u1")

    assert result is not None
    assert result.name == "Alice"
```

## Coverage Configuration

Minimum 80% line coverage on `src/`. Critical modules (payments, auth) must have 100%:

```toml
[tool.coverage.report]
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "@abstractmethod",
    "raise NotImplementedError",
]
```
