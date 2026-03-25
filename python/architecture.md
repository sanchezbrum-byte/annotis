# Python Architecture

## Project Structure

See `universal/architecture.md` for the full Clean Architecture description. The Python-specific folder structure:

```
src/
  myapp/
    domain/
      __init__.py
      order.py            # Order entity + domain rules
      user.py
      value_objects.py    # OrderId, Money, Address
      exceptions.py       # DomainError hierarchy
      ports/
        order_repository.py    # Abstract base class / Protocol
        payment_gateway.py
        event_bus.py
    application/
      __init__.py
      submit_order.py         # SubmitOrderUseCase
      cancel_order.py
      dtos.py                 # Input/output data transfer objects
    adapters/
      http/
        routers/
          orders.py       # FastAPI router
        schemas/
          order_schemas.py  # Pydantic request/response models
      persistence/
        models.py           # SQLAlchemy ORM models
        order_repository.py  # Implements domain port
        migrations/         # Alembic migrations
      messaging/
        order_events.py     # Kafka producer/consumer
    shared/
      config.py
      logging.py
      exceptions.py
      middleware.py
  main.py                 # FastAPI app factory
tests/
  conftest.py
  unit/
  integration/
  e2e/
pyproject.toml
```

## Dependency Injection

Use constructor injection — not `get_db()` calls inside functions:

```python
# ❌ BAD: implicit global dependency
from myapp.adapters.persistence import get_session

class OrderService:
    def submit(self, order_id: str) -> None:
        session = get_session()  # Global; impossible to test without patching
        order = session.query(Order).filter_by(id=order_id).first()

# ✅ GOOD: explicit injection
class SubmitOrderUseCase:
    def __init__(
        self,
        order_repo: OrderRepository,
        event_bus: EventBus,
    ) -> None:
        self._order_repo = order_repo
        self._event_bus = event_bus

    def execute(self, order_id: str, user_id: str) -> OrderConfirmation:
        order = self._order_repo.find(order_id)
        order.submit()
        self._order_repo.save(order)
        self._event_bus.publish(OrderSubmittedEvent(order.id))
        return OrderConfirmation.from_order(order)
```

## Ports as Protocols (Python 3.8+)

Use `typing.Protocol` for port definitions (structural typing, no inheritance needed):

```python
# domain/ports/order_repository.py
from typing import Protocol
from myapp.domain.order import Order

class OrderRepository(Protocol):
    def find(self, order_id: str) -> Order | None: ...
    def save(self, order: Order) -> None: ...
    def find_by_user(self, user_id: str) -> list[Order]: ...

# adapters/persistence/postgres_order_repo.py
class PostgresOrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find(self, order_id: str) -> Order | None:
        model = self._session.get(OrderModel, order_id)
        return Order.from_model(model) if model else None

    def save(self, order: Order) -> None:
        model = OrderModel.from_domain(order)
        self._session.merge(model)
```
