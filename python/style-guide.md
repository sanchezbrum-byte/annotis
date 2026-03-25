# Python Style Guide

> **Sources:** PEP 8 (Guido van Rossum), PEP 257 (Goodger & van Rossum), Google Python Style Guide (google.github.io/styleguide/pyguide.html), Black formatter defaults, Ruff linter rules

---

## A. Formatting & Style

### Line Length

| Limit | Value | Rationale |
|-------|-------|-----------|
| **Hard limit** | **88 characters** | Black formatter default; fits two files side-by-side on modern screens |
| **Soft limit** | **79 characters** | PEP 8 recommendation; strive for this, especially in comments/docstrings |

> PEP 8 specifies 79 characters. Black uses 88. The Google Python Style Guide uses 80. We adopt Black's 88 as the hard limit to be compatible with auto-formatting, and treat 79 as the target for human-written lines.

### Maximum Function Length

- **50 lines** maximum per function (excluding docstrings and blank lines)
- Functions exceeding 50 lines should be split into smaller, focused helpers
- If splitting produces many private helpers, consider whether a class with methods would be more readable

### Maximum File Length

- **1000 lines** maximum per file (Google Python Style Guide)
- If a module exceeds 1000 lines, split by concept — not arbitrarily

### Indentation

- **4 spaces** per level — never tabs (PEP 8)
- Continuation lines aligned with opening delimiter, or hanging indent of 4 spaces:

```python
# ✅ Aligned with opening delimiter
result = some_function(
    argument_one,
    argument_two,
    argument_three,
)

# ✅ Hanging indent (4 spaces)
result = some_function(
    argument_one, argument_two,
    argument_three,
)

# ❌ No indentation on continuation
result = some_function(argument_one,
argument_two)
```

### Blank Lines

- **2 blank lines** before and after top-level function and class definitions (PEP 8)
- **1 blank line** between methods inside a class
- **1 blank line** to separate logical sections within a function
- No trailing whitespace on any line

### Import Ordering (isort / Ruff)

```python
# Group 1: Standard library
import os
import sys
from datetime import datetime, timezone
from typing import Optional

# Group 2: Third-party packages (blank line between groups)
import httpx
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# Group 3: Local application imports (blank line between groups)
from myapp.domain.user import User
from myapp.infrastructure.database import get_session
```

- No wildcard imports: `from module import *` is **forbidden** (PEP 8)
- Absolute imports preferred over relative imports (PEP 8, Google guide)
- One import per line for `import x` style; multiple allowed for `from x import a, b`

### Trailing Commas

Use trailing commas in multi-line collections and function signatures:

```python
# ✅ GOOD — trailing comma enables clean diffs
SUPPORTED_CURRENCIES = [
    "USD",
    "EUR",
    "GBP",
]

def create_order(
    user_id: str,
    items: list[OrderItem],
    currency: str = "USD",
) -> Order:
    ...
```

### Semicolons

**Never use semicolons** to combine statements on one line (PEP 8).

---

## B. Naming Conventions

| Concept | Convention | Example |
|---------|-----------|---------|
| Variables | `snake_case` | `user_id`, `total_price` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Functions | `snake_case` | `calculate_total`, `get_user` |
| Classes | `PascalCase` | `OrderService`, `PaymentResult` |
| Modules/files | `snake_case` | `order_service.py`, `payment_processor.py` |
| Packages | `lowercase` | `myapp`, `utils` |
| Type aliases | `PascalCase` | `UserId = str` |
| Private | leading `_` | `_validate_input`, `_cache` |
| Name-mangled | leading `__` | Only when truly private to a class |
| "Protected" dunder | `__dunder__` | Only for Python special methods |

### Boolean Naming

```python
# ✅ GOOD
is_authenticated = True
has_active_subscription = False
should_retry = True
can_edit_post = False

# ❌ BAD
authenticated = True
subscription = False
retry = True
edit = False
```

### Abbreviations

**Allowed:** `id`, `url`, `api`, `http`, `db`, `cfg`, `tmp`, `msg`, `req`, `res`, `err`

**Forbidden:** Domain-specific or opaque abbreviations — spell them out:
```python
# ❌ BAD
usr_mgr = UserManager()
crt_ord = create_order()
pmnt_prc = PaymentProcessor()

# ✅ GOOD
user_manager = UserManager()
order = create_order()
payment_processor = PaymentProcessor()
```

### Test Function Naming

```python
def test_<function>_<scenario>_<expected>():

# Examples:
def test_calculate_total_with_discount_returns_discounted_amount():
def test_calculate_total_with_empty_cart_returns_zero():
def test_charge_card_when_expired_raises_payment_error():
def test_find_user_when_not_found_returns_none():
def test_create_order_with_invalid_currency_raises_value_error():
```

---

## C. Functions & Methods

### Single Responsibility

One function = one task. If you need to use "and" or "or" to describe what a function does, split it.

```python
# ❌ BAD: two responsibilities
def register_user_and_send_welcome(email: str, password: str) -> User:
    user = create_user(email, password)
    send_welcome_email(user)  # side effect mixed with creation
    return user

# ✅ GOOD: separated
def create_user(email: str, password: str) -> User:
    ...

def send_welcome_email(user: User) -> None:
    ...
```

### Maximum Parameters

**Maximum 5 parameters.** If a function needs more, use a dataclass or TypedDict:

```python
# ❌ BAD: too many parameters (hard to call, hard to read)
def create_order(
    user_id: str, item_ids: list[str], currency: str,
    discount_code: str, shipping_address: str, payment_method: str,
) -> Order:
    ...

# ✅ GOOD: group into a value object
@dataclass(frozen=True)
class CreateOrderRequest:
    user_id: str
    item_ids: list[str]
    currency: str
    discount_code: str | None
    shipping_address: Address
    payment_method: PaymentMethod

def create_order(request: CreateOrderRequest) -> Order:
    ...
```

### Return Types — Always Explicit

All functions must have explicit return type annotations:

```python
# ❌ BAD — caller cannot know return type without reading implementation
def get_user(user_id):
    ...

# ✅ GOOD
def get_user(user_id: str) -> User | None:
    ...

def process_payment(amount: Decimal) -> PaymentResult:
    ...

def send_notification(user: User) -> None:
    ...
```

### Early Returns Over Deep Nesting

Prefer guard clauses (early returns) over nested conditionals:

```python
# ❌ BAD: deep nesting
def process_order(order: Order) -> OrderResult:
    if order is not None:
        if order.is_valid():
            if order.user.has_active_subscription():
                return execute_order(order)
            else:
                return OrderResult.failure("No active subscription")
        else:
            return OrderResult.failure("Invalid order")
    else:
        return OrderResult.failure("Order not found")

# ✅ GOOD: early returns flatten the code
def process_order(order: Order | None) -> OrderResult:
    if order is None:
        return OrderResult.failure("Order not found")
    if not order.is_valid():
        return OrderResult.failure("Invalid order")
    if not order.user.has_active_subscription():
        return OrderResult.failure("No active subscription")
    return execute_order(order)
```

---

## D. Comments & Documentation

### Google-Style Docstrings (Required for all public functions)

```python
def calculate_refund(
    order: Order,
    reason: RefundReason,
    amount: Decimal | None = None,
) -> RefundResult:
    """Calculate and process a refund for a given order.

    Applies the refund policy based on the order age and reason.
    Partial refunds are supported by specifying an amount.

    Args:
        order: The order to refund. Must be in COMPLETED status.
        reason: The reason for the refund, used to determine policy eligibility.
        amount: Optional partial refund amount. If None, full refund is issued.
            Must be positive and ≤ order.total.

    Returns:
        A RefundResult containing the refund_id, amount, and processing status.

    Raises:
        RefundNotEligibleError: If the order is not eligible for a refund
            (e.g., older than the refund window or already refunded).
        ValueError: If amount is negative or exceeds the order total.

    Example:
        >>> result = calculate_refund(order, RefundReason.DAMAGED, Decimal("25.00"))
        >>> print(result.refund_id)
        'rfnd_abc123'
    """
```

### Inline Comments

```python
# ✅ GOOD: explains WHY (non-obvious reasoning)
# Stripe requires idempotency keys for retry safety. Use date-based key
# so a crash-and-retry within the same day reuses the same attempt.
idempotency_key = f"{order.id}:{date.today().isoformat()}"

# ❌ BAD: explains WHAT (redundant with code)
# Increment retry count
retry_count += 1

# ❌ BAD: commented-out dead code
# old_total = sum(item.price for item in order.items)
```

### TODO/FIXME Format

```python
# TODO(alice@example.com, 2025-03-15, INFRA-423): Replace sync client with
# async client after upgrading to httpx 0.28+.
response = http_client.get_sync(url)

# FIXME(bob@example.com, 2025-02-01, PAY-887): Integer overflow risk for
# orders exceeding $999,999. Migrate to Decimal arithmetic.
total_cents = price_cents * quantity
```

---

## E. Error Handling

### Specific Exceptions

```python
# ❌ BAD: bare except catches everything including KeyboardInterrupt
try:
    result = risky_operation()
except:
    pass

# ❌ BAD: swallows the error silently
try:
    result = risky_operation()
except Exception:
    pass

# ✅ GOOD: specific exception, logged, re-raised or handled
try:
    result = payment_gateway.charge(amount, card_token)
except GatewayTimeoutError as e:
    logger.warning("Payment gateway timeout", extra={"order_id": order_id, "error": str(e)})
    raise PaymentServiceUnavailableError("Payment service is temporarily unavailable") from e
except GatewayDeclineError as e:
    logger.info("Payment declined", extra={"order_id": order_id, "code": e.decline_code})
    raise PaymentDeclinedError(e.decline_code) from e
```

### Custom Exception Hierarchy

```python
# Define domain-specific exception hierarchy
class AppError(Exception):
    """Base exception for all application errors."""

class DomainError(AppError):
    """Business rule violations."""

class PaymentError(DomainError):
    """Payment-related business errors."""

class PaymentDeclinedError(PaymentError):
    def __init__(self, decline_code: str):
        self.decline_code = decline_code
        super().__init__(f"Payment declined: {decline_code}")

class InfrastructureError(AppError):
    """External service failures."""

class PaymentServiceUnavailableError(InfrastructureError):
    """Payment gateway is unreachable."""
```

### Validation at the Boundary

```python
# ✅ GOOD: Use Pydantic for boundary validation
from pydantic import BaseModel, EmailStr, field_validator
from decimal import Decimal

class CreateOrderRequest(BaseModel):
    user_id: str
    amount: Decimal
    currency: str
    email: EmailStr

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @field_validator("currency")
    @classmethod
    def currency_must_be_supported(cls, v: str) -> str:
        if v not in {"USD", "EUR", "GBP"}:
            raise ValueError(f"Unsupported currency: {v}")
        return v
```

---

## F. Imports & Dependencies

- Import ordering: stdlib → third-party → local (enforced by isort / Ruff)
- No wildcard imports (`from module import *`)
- Prefer absolute imports over relative
- Use `TYPE_CHECKING` guard for imports only needed for type annotations:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from myapp.domain.order import Order
```

---

## G. Architecture Rules

### Recommended Project Structure

```
src/
  myapp/
    domain/         # Entities, value objects, domain services, ports (interfaces)
    application/    # Use cases, application services, DTOs
    adapters/
      http/         # FastAPI/Flask routers, request/response models
      persistence/  # SQLAlchemy models, repositories
      messaging/    # Kafka/RabbitMQ producers/consumers
    shared/         # Shared utilities: logging, config, exceptions
tests/
  unit/
  integration/
  e2e/
pyproject.toml
```

### Rules

- No database calls in domain entities — entities are pure Python, no ORM dependencies
- No HTTP logic in use cases — use cases call ports (interfaces), not HTTP clients directly
- Use dependency injection — pass dependencies as constructor arguments, not global singletons

---

## H. Performance

### String Building

```python
# ❌ BAD: O(n²) string concatenation in loop
result = ""
for row in rows:
    result += row.to_csv_line() + "\n"

# ✅ GOOD: O(n) join
result = "\n".join(row.to_csv_line() for row in rows)
```

### Comprehensions vs Generators

```python
# Use list comprehension when you need random access or multiple iterations
user_ids = [u.id for u in users]

# Use generator when iterating once or passing to another iterator
total = sum(item.price for item in cart.items)  # generator — no list created
```

### Avoiding Global State

```python
# ❌ BAD: module-level mutable state
_user_cache = {}  # mutable global — causes subtle bugs in tests and concurrent code

# ✅ GOOD: encapsulate in a class or use an explicit cache object
class UserCache:
    def __init__(self) -> None:
        self._cache: dict[str, User] = {}
```

---

## I. Security

### SQL Injection Prevention

```python
# ❌ BAD: f-string in SQL query
query = f"SELECT * FROM users WHERE email = '{email}'"
cursor.execute(query)

# ✅ GOOD: parameterized query
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

# ✅ GOOD: SQLAlchemy ORM (automatic parameterization)
user = session.query(User).filter(User.email == email).first()
```

### Secrets

```python
# ❌ BAD: hardcoded secret
DATABASE_URL = "postgresql://admin:hunter2@prod.db/myapp"

# ✅ GOOD: environment variable
import os
DATABASE_URL = os.environ["DATABASE_URL"]

# ✅ BEST: secret manager for production
from myapp.config import settings  # loaded from AWS Secrets Manager at startup
DATABASE_URL = settings.database_url
```

### Dependency Scanning

```bash
# Run in CI before deploying
pip-audit --requirement requirements.txt --strict
```

### Deserialization Safety

```python
# ❌ BAD: pickle from untrusted source = arbitrary code execution
data = pickle.loads(user_supplied_bytes)

# ✅ GOOD: use JSON for untrusted data
data = json.loads(user_supplied_string)
# Use Pydantic to validate schema after parsing
parsed = MyModel.model_validate(data)
```
