# Python AI Rules

> Full reference: `python/style-guide.md`

---

## Formatting (Black + PEP 8)

- Hard line limit: **88 chars** (Black default) — use `line-length = 88` in pyproject.toml
- Indentation: **4 spaces** (never tabs)
- Import order: stdlib → third-party → local (enforced by Ruff/isort)
- No wildcard imports (`from module import *`)
- Trailing commas in multi-line function signatures and collections

## Naming

| Concept | Style | Example |
|---------|-------|---------|
| Variables/functions | `snake_case` | `get_user`, `total_price` |
| Classes | `PascalCase` | `OrderService` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Booleans | `is_`, `has_`, `can_`, `should_` | `is_active`, `has_subscription` |
| Tests | `test_<method>_<scenario>_<expected>` | `test_charge_expired_card_raises_payment_error` |

## Functions

- Max **50 lines** per function (excluding docstrings)
- Max **5 parameters** — use `@dataclass` if more needed
- Always explicit return type annotations: `def get_user(id: str) -> User | None:`
- Prefer early returns (guard clauses) over deep nesting
- Never `except:` or `except Exception: pass` — always specific + logged

## Documentation (Google Style)

```python
def calculate_refund(order: Order, amount: Decimal | None = None) -> RefundResult:
    """Calculate and process a refund.

    Args:
        order: The order to refund. Must be in COMPLETED status.
        amount: Optional partial amount. Defaults to full refund.

    Returns:
        RefundResult with refund_id and status.

    Raises:
        RefundNotEligibleError: If order is not eligible.
    """
```

## Type Safety

- `mypy --strict` must pass — no untyped code in production
- Use `pydantic` for boundary validation (HTTP request bodies, config)
- Use `Protocol` for structural typing of ports/interfaces
- Prefer `X | None` over `Optional[X]` (Python 3.10+)

## Error Handling

```python
# ✅ Specific, logged, re-raised
try:
    result = payment_gateway.charge(amount, token)
except GatewayTimeoutError as e:
    logger.warning("Gateway timeout", extra={"order_id": order_id})
    raise PaymentServiceUnavailableError() from e

# ❌ Never
except:
    pass
```

## Security

- No `eval()`, `pickle.loads()` on untrusted data
- Parameterized SQL: `cursor.execute("SELECT ... WHERE id = %s", (id,))`
- Secrets from env: `os.environ["SECRET_KEY"]` — never hardcoded
- Run `pip-audit` in CI

## Tooling

```bash
black .           # format
ruff check .      # lint (replaces flake8, isort, pyupgrade)
mypy .            # type check
pytest --cov=src  # test with coverage
pip-audit         # security scan
```
