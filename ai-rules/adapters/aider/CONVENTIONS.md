# Engineering Conventions — loaded automatically by Aider

> Auto-generated from ai-rules/core/. Do not edit directly.
> Edit core/ files and run sync-adapters.sh to regenerate.

---

# Universal Engineering Rules

> Single source of truth — applies to ALL languages and projects.
> Full reference: `universal/` directory.

---

## Commit Message Format (Conventional Commits v1.0.0)

```
<type>[(scope)]: <description>     ← max 72 chars; imperative mood
                                    ← blank line
[body]                              ← explains WHY, not WHAT
                                    ← blank line
[footer]                            ← Closes: #123, BREAKING CHANGE: ...
```

Types: `feat` `fix` `docs` `style` `refactor` `perf` `test` `chore` `ci` `build` `revert`

✅ `feat(auth): add OAuth2 PKCE flow for mobile clients`
✅ `fix(payment): prevent double-charge on network timeout retry`
❌ `fixed stuff` / `WIP` / `update` / `various fixes`

Breaking change: `feat!: remove deprecated /api/v1 endpoints`

---

## Corner Case Checklist

Before marking any task complete, verify test coverage for:

- [ ] `null` / `nil` / `None` / `undefined` inputs
- [ ] Empty collections (`[]`, `{}`, `""`)
- [ ] Single-element collections
- [ ] Boundary values: `0`, `1`, `max_int`, `min_int`, `-1`
- [ ] Very large inputs (10M+ items)
- [ ] Negative numbers where positive expected
- [ ] Unicode / non-ASCII / emoji inputs
- [ ] Whitespace-only strings
- [ ] Concurrent/parallel execution
- [ ] Network failure / timeout scenarios
- [ ] Partial failures in multi-step operations
- [ ] Idempotency (calling twice = same result)

---

## Code Quality Rules

### Never in commits:
- `print()`, `console.log()`, `fmt.Println()`, `println!()`, `System.out.println()` debug output
- Commented-out dead code (delete it — git history preserves it)
- TODO without `(author, date, ticket)` reference
- Hardcoded secrets, passwords, API keys, tokens

### Every new function requires:
- At least one test covering the happy path
- At least one test covering the primary error case
- Docstring/JSDoc/GoDoc for all public functions

---

## Security Rules (Non-Negotiable)

```
NEVER hardcode:
  - API keys / tokens
  - Database passwords
  - Private keys / certificates
  - OAuth client secrets

ALWAYS:
  - Use env vars or secret managers for secrets
  - Parameterize SQL queries (never string concatenation)
  - Validate inputs at the boundary (HTTP layer, CLI args)
  - Check authorization on every data access operation
```

---

## Performance Rules

- Always comment Big-O complexity for non-trivial algorithms
- Prefer O(n) or O(n log n) over O(n²) — explain if O(n²) is acceptable
- Avoid N+1 query patterns — load related data in one query
- No string concatenation in loops — use builders/join
- Profile before optimizing critical paths

---

## Architecture Rules

- Dependency direction: inward only (infrastructure → application → domain)
- No database calls in domain entities
- No HTTP calls in use cases (use port interfaces)
- No business logic in HTTP controllers
- Validate at the boundary; trust inside the boundary

---

## Code Review Requirements

- PR size: ≤ 400 lines changed (Google recommendation)
- All CI checks pass before requesting review
- No self-merges without at least 1 reviewer approval
- Blocking comments: `[blocking]` must be resolved before merge
- Non-blocking suggestions: `[nit]` author's discretion

---

## Testing Requirements

| Code Type | Min Coverage |
|-----------|-------------|
| Business logic | 80% line coverage |
| Critical paths (auth, payments, data integrity) | 100% |
| Infrastructure adapters | 60% |

Test naming: `<method>_<scenario>_<expected_behavior>`

---

# Git Workflow AI Rules

> Full reference: `universal/git-workflow.md`

---

## Commit Format (Conventional Commits v1.0.0)

```
<type>[(scope)]: <description>
                               ← blank line
[body — explains WHY]
                               ← blank line
[footer — Closes: #123, BREAKING CHANGE: ...]
```

**Types:** `feat` `fix` `docs` `style` `refactor` `perf` `test` `chore` `ci` `build` `revert`

**Rules:**
- Subject: imperative mood, max **72 chars**, no period
- Body: wrap at 72 chars; explains WHY, not WHAT
- `feat!:` or `BREAKING CHANGE:` footer for breaking changes

**Examples:**
```
feat(auth): add OAuth2 PKCE flow for mobile clients
fix(pay): prevent double-charge on network timeout retry
docs: update getting-started guide with Docker Compose setup
chore(deps): bump axios from 1.6.0 to 1.7.2
```

---

## Branch Naming

```
feat/AUTH-123-oauth2-pkce
fix/PAY-456-double-charge-retry
hotfix/SEC-789-xss-in-markdown-renderer
release/v2.4.0
chore/update-node-20
```

Rules: lowercase, hyphens only, include ticket number when available

---

## SemVer Tagging

- `MAJOR.MINOR.PATCH`
- MAJOR: breaking change; MINOR: new feature; PATCH: bug fix
- Always use annotated tags: `git tag -a v2.4.0 -m "release: v2.4.0"`

---

## PR Rules

- Max **400 lines changed** per PR (Google recommendation)
- Self-review before requesting reviewer
- CI must pass before requesting review
- Reviewer responds within **1 business day**

---

## Never Commit

- Secrets, API keys, passwords, tokens
- `.env` files with real values
- `node_modules/`, `__pycache__/`, `*.pyc`, `target/`, `dist/`
- `.DS_Store`, IDE files (unless sharing settings intentionally)
- Compiled binaries, large files > 50 MB

---

## Merge Strategy

| Situation | Strategy |
|-----------|---------|
| Feature branch → main | **Squash and merge** |
| Release branch → main | **Merge commit** |
| Never on shared branches | **rebase --force-push** |

---

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

---

# Security AI Rules

> Full reference: `universal/security.md`

---

## OWASP Top 10:2021 — Quick Reference

| # | Vulnerability | Prevention |
|---|--------------|-----------|
| A01 | Broken Access Control | Check authorization on every data access, not just auth |
| A02 | Cryptographic Failures | TLS 1.2+, bcrypt/Argon2 for passwords, AES-256 at rest |
| A03 | Injection | Parameterized queries, `never` string concatenation in SQL |
| A04 | Insecure Design | Threat model new features handling sensitive data |
| A05 | Security Misconfiguration | No default passwords, disable unused features, hide errors |
| A06 | Vulnerable Components | `npm audit`, `pip-audit`, `cargo audit` in CI |
| A07 | Auth Failures | Rate limiting on auth, MFA, strong session management |
| A08 | Software Integrity | Verify package checksums, sign artifacts |
| A09 | Logging Failures | Log auth events, failures; never log secrets/PII |
| A10 | SSRF | Allowlist for server-side HTTP requests |

---

## Non-Negotiable Rules

### Secrets

```python
# ❌ CRITICAL: never hardcode
API_KEY = "sk_live_hardcoded_abc123"

# ✅ Always from environment or secret manager
API_KEY = os.environ["STRIPE_API_KEY"]
```

### SQL Injection

```python
# ❌ CRITICAL: string concatenation
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ Parameterized
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

### Authentication

```python
# ❌ Trusting user-supplied ID
@router.get("/orders/{order_id}")
def get_order(order_id: str, user_id: str = Body(...)):

# ✅ User identity from validated JWT/session
@router.get("/orders/{order_id}")
def get_order(order_id: str, user: User = Depends(require_auth)):
    if order.owner_id != user.id:
        raise ForbiddenError()
```

### Password Hashing

```python
# ❌ NEVER: MD5, SHA1, SHA256 for passwords
hashed = hashlib.md5(password.encode()).hexdigest()

# ✅ Always: bcrypt, Argon2, or scrypt
hashed = bcrypt.hash(password, rounds=12)
```

---

## Never Log

- Passwords, PINs, security answers
- Full credit card numbers
- Authentication tokens, session IDs
- API keys, private keys
- Full SSNs, PHI, unmasked PII

## Do Log (Security Events)

- Authentication success/failure (with IP, timestamp)
- Authorization failures
- Input validation failures
- Admin/privileged actions

---

# Architecture AI Rules

> Full reference: `universal/architecture.md`

---

## SOLID Principles

| Principle | Rule | Red Flag |
|-----------|------|---------|
| **S**RP | One class = one reason to change | "and" in function description |
| **O**CP | Open for extension, closed for modification | `if/else` chain growing for new types |
| **L**SP | Subclass can substitute parent without breaking behavior | Subclass throws on parent's valid inputs |
| **I**SP | Small, focused interfaces over large general ones | Implementing empty methods |
| **D**IP | Depend on abstractions, not concretions | `new ConcreteService()` inside business logic |

---

## Dependency Direction (Clean Architecture)

```
Frameworks → Adapters → Use Cases → Entities
                                   (Domain)
```

**Rule: dependencies point INWARD only.**

```python
# ❌ Domain entity depends on infrastructure
class Order:
    def save(self):
        db.execute("INSERT INTO orders ...")  # domain knows about DB!

# ✅ Use case depends on port interface (abstraction)
class SubmitOrderUseCase:
    def __init__(self, repo: OrderRepository):  # interface, not concrete
        self._repo = repo
```

---

## Layer Rules

| Layer | Contains | Must NOT contain |
|-------|----------|-----------------|
| Entities | Domain objects, business rules | Framework imports, DB queries, HTTP |
| Use Cases | Application business rules | Framework imports, DB drivers, UI |
| Adapters | Controllers, repositories, mappers | Business rules |
| Frameworks | Express, Spring, SQLAlchemy | Business rules |

---

## Design Patterns — When to Use

```
Strategy  → multiple interchangeable algorithms
Factory   → complex object creation
Repository → abstract data persistence
Observer  → multiple consumers of an event

Anti-patterns to avoid:
God Object → one class does everything → apply SRP
Anemic Domain Model → all logic in services, domain is data bags
Service Locator → global dependency lookup → use constructor injection
```

---

## Abstraction Rules (Rule of Three)

- **1st occurrence:** implement directly
- **2nd occurrence:** note the duplication
- **3rd occurrence:** create shared abstraction

Before adding an interface, check:
- [ ] Are there 2+ concrete implementations now (or in tests)?
- [ ] Does the name describe a concept, not just wrap a class?
- [ ] Will callers depend on the abstraction, not the concrete?

---

## Microservices vs Monolith

Start with a **monolith**. Extract services when:
- Genuinely different scaling requirements
- Different deployment cadences
- Team autonomy requires it (team of 6+)
- Regulatory isolation needed

**Never** extract services because "it seems like it should be separate."

---

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

---

# JavaScript AI Rules

> Full reference: `javascript/style-guide.md`

---

## Formatting (Airbnb + Prettier)

- Hard line limit: **100 chars** (Airbnb)
- Indentation: **2 spaces**
- Semicolons: **required**
- Quotes: **single** (`'string'`), backticks for templates
- Trailing commas: required in multi-line
- Always use braces even for single-line `if`

## Variables

```javascript
const MAX_RETRIES = 3;          // ✅ const by default
let retryCount = 0;             // ✅ let when reassigned
// var — FORBIDDEN (no-var ESLint rule)
```

## Naming

| Concept | Style | Example |
|---------|-------|---------|
| Variables/functions | `camelCase` | `getUser`, `totalPrice` |
| Classes | `PascalCase` | `OrderService` |
| Constants (module-level) | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Files | `camelCase` or `kebab-case` | `orderService.js` |
| Booleans | `is/has/can/should` | `isAuthenticated` |

## Functions

- Max **4 parameters** — use options object for more
- Prefer arrow functions for callbacks; named functions for top-level
- Early returns over deep nesting
- `async/await` over `.then()` chains
- `Promise.all()` for parallel independent async operations

## Error Handling

```javascript
// ✅ Specific error types, logged, translated
try {
  return await stripe.charges.create({ amount, source: token });
} catch (error) {
  if (error.type === 'StripeCardError') {
    logger.info('Card declined', { orderId, code: error.code });
    throw new PaymentDeclinedError(error.code);
  }
  logger.error('Stripe error', { orderId, error: error.message });
  throw new PaymentServiceError('Service unavailable');
}

// ❌ Never throw non-Error objects
throw 'Payment failed';  // BAD — always: throw new Error(...)
```

## Security

```javascript
// ❌ CRITICAL: never eval user input
eval(userInput);           // arbitrary code execution

// ✅ SQL: use parameterized queries
db.query('SELECT * FROM users WHERE email = $1', [email]);

// ✅ Secrets: from process.env only
const apiKey = process.env.STRIPE_API_KEY;
```

## ES Module Imports

```javascript
// ✅ ES Modules (preferred)
import { calculateTotal } from './utils.js';
export function processOrder(order) { ... }

// CommonJS only for legacy code
const { processOrder } = require('./orderService');
```

## Tooling

```bash
eslint . --fix        # lint
prettier --write .    # format
jest --coverage       # test
npm audit             # security scan
```

---

# TypeScript AI Rules

> Inherits all JavaScript rules. Full reference: `typescript/style-guide.md`

---

## Type System (Non-Negotiable)

```json
// tsconfig.json — required settings
{
  "strict": true,
  "noUncheckedIndexedAccess": true,
  "noImplicitReturns": true
}
```

**Forbidden:**
- `any` type — use `unknown` + type guards, or `z.infer<Schema>` from Zod
- `as` assertions — use type guards or `satisfies`
- `!` non-null assertions — use `?.` or guard clauses
- `enum` — use `const` object + `typeof` instead

## Naming

| Concept | Style | Example |
|---------|-------|---------|
| Interfaces | `PascalCase` (no `I` prefix) | `User`, `OrderRepository` |
| Type aliases | `PascalCase` | `PaymentStatus`, `UserId` |
| Generic params | Single letter or `TName` | `T`, `TEntity`, `TKey` |

## Interfaces vs Type Aliases

```typescript
// ✅ Interface for object shapes (extendable)
interface User { id: string; name: string; }

// ✅ Type for unions, intersections, mapped types
type PaymentStatus = 'pending' | 'paid' | 'failed';
type OrderWithUser = Order & { user: User };
```

## Enums → Const Objects

```typescript
// ❌ enum (avoid)
enum OrderStatus { Pending = 'pending', Paid = 'paid' }

// ✅ const object + typeof
const OrderStatus = { Pending: 'pending', Paid: 'paid' } as const;
type OrderStatus = typeof OrderStatus[keyof typeof OrderStatus];
```

## Zod for Boundary Validation

```typescript
const CreateOrderSchema = z.object({
  userId: z.string().uuid(),
  items: z.array(OrderItemSchema).min(1),
  currency: z.enum(['USD', 'EUR', 'GBP']),
});
type CreateOrderDto = z.infer<typeof CreateOrderSchema>;
```

## Explicit Return Types

```typescript
// ✅ Always annotate public function return types
async function getUser(id: string): Promise<User | null> { ... }
function formatPrice(amount: number): string { ... }
```

## Exhaustive Switch

```typescript
// ✅ Discriminated union — compiler catches missing cases
switch (status.kind) {
  case 'pending': return ...;
  case 'paid': return ...;
  default: {
    const _exhaustive: never = status;
    throw new Error(`Unknown status: ${JSON.stringify(_exhaustive)}`);
  }
}
```

## Tooling

```bash
tsc --noEmit          # type check
eslint . --fix        # lint (with @typescript-eslint/strict)
prettier --write .    # format
vitest --coverage     # test
npm audit             # security scan
```

---

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

---

# Go AI Rules

> Full reference: `go/style-guide.md`

---

## Formatting (gofmt)

- gofmt manages ALL formatting — no debates, no configuration
- Indentation: **tabs** (enforced by gofmt)
- Line length: no hard limit; keep < 100 chars as soft target
- Import groups: stdlib → external → internal (goimports manages)

## Naming (Effective Go)

| Concept | Style | Example |
|---------|-------|---------|
| Exported | `PascalCase` | `OrderService`, `ProcessPayment` |
| Unexported | `camelCase` | `orderRepo`, `processPayment` |
| Packages | `lowercase` (no underscores) | `orders`, `payment` |
| Interfaces (1 method) | Method + `er` | `Reader`, `Writer`, `Closer` |
| Error vars | `Err` prefix | `ErrOrderNotFound` |
| Acronyms | consistent case | `userID`, `orderURL`, `parseJSON` |

## Error Handling

```go
// ✅ Always handle errors — never ignore with _
result, err := repo.FindByID(ctx, id)
if err != nil {
    return fmt.Errorf("finding order %s: %w", id, err)
}
if result == nil {
    return ErrOrderNotFound
}

// ❌ NEVER
result, _ := repo.FindByID(ctx, id)  // ignores error
```

## Function Design

- Max ~40 lines per function
- Accept interfaces, return concrete types (Uber Go Style)
- Error is always the last return value
- Small, focused interfaces (prefer 1–3 methods)
- Context is first parameter for all cancelable operations

```go
// ✅ Accept interface, return concrete
func NewOrderService(repo OrderRepository, gw PaymentGateway) *OrderService { ... }

// ✅ Context first, error last
func (s *Service) ProcessPayment(ctx context.Context, id, token string) (*Confirmation, error)
```

## Concurrency

```go
// ✅ goroutine ownership: document who stops it
// ✅ always run tests with -race flag
// ✅ use sync.Mutex for shared state; channels for communication
// ✅ use context for cancellation propagation
// ❌ never spawn goroutine without knowing how it terminates
```

## Security

```go
// ✅ Parameterized SQL
row := pool.QueryRow(ctx, "SELECT * FROM users WHERE email = $1", email)

// ❌ String interpolation in SQL
query := fmt.Sprintf("SELECT * FROM users WHERE email = '%s'", email) // SQLi!

// ✅ Secrets from environment
dbURL := os.Getenv("DATABASE_URL")
if dbURL == "" { log.Fatal("DATABASE_URL must be set") }
```

## Tooling

```bash
goimports -l -w .     # format + organize imports
go vet ./...          # built-in analysis
staticcheck ./...     # advanced static analysis
go test -race ./...   # tests with race detector
govulncheck ./...     # security vulnerability scan
```

---

# Rust AI Rules

> Full reference: `rust/style-guide.md`

---

## Formatting (rustfmt)

- Line limit: **100 chars** (`max_width = 100`)
- Indentation: **4 spaces**
- Use `cargo fmt` — no manual formatting debates
- Import grouping: std → external → local (rustfmt manages)

## Naming (Rust API Guidelines)

| Concept | Style | Example |
|---------|-------|---------|
| Functions/methods | `snake_case` | `process_payment`, `find_by_id` |
| Types (struct/enum/trait) | `PascalCase` | `Order`, `PaymentError` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_RETRIES` |
| Modules | `snake_case` | `order_service`, `payment_gateway` |
| Conversion methods | `from_`, `into_`, `to_`, `as_` | `Order::from_row`, `to_string` |

## Error Handling

```rust
// ✅ thiserror for library errors
#[derive(Debug, Error)]
pub enum PaymentError {
    #[error("Order {0} not found")] OrderNotFound(String),
    #[error("Card declined: {code}")] Declined { code: String },
    #[error("Service unavailable")] ServiceUnavailable(#[source] reqwest::Error),
}

// ✅ anyhow for application error propagation
use anyhow::{Context, Result};
let config = Config::from_env().context("Failed to load config")?;

// ❌ NEVER unwrap/expect in library code
let order = repo.find(id).unwrap(); // panics → crashes caller
```

## Ownership Patterns

```rust
// ✅ Pass by reference for read-only
fn log_order(order: &Order) { ... }

// ✅ Pass by value + move for ownership transfer
fn process(order: Order) { ... }

// ✅ Arc<RwLock<T>> for shared mutable state in async
let state = Arc::new(RwLock::new(AppState::default()));
```

## Unsafe Code

Every `unsafe` block MUST have a `// SAFETY:` comment:
```rust
// SAFETY: pointer was created by Box::into_raw, exclusive access guaranteed
let value = unsafe { Box::from_raw(ptr) };
```

## panic! Policy

| Context | `unwrap()`/`panic!()` |
|---------|-----------------------|
| Tests | ✅ Allowed |
| CLI entry point | ✅ With descriptive `expect()` message |
| Library code | ❌ Never — return `Result` |
| Business logic | ❌ Never |

## Security

```rust
// ✅ Parameterized SQL (sqlx)
let user = sqlx::query_as!(User, "SELECT * FROM users WHERE email = $1", email)
    .fetch_optional(&pool).await?;

// ✅ Secrets from environment
let db_url = std::env::var("DATABASE_URL")
    .expect("DATABASE_URL must be set");
```

## Tooling

```bash
cargo fmt                    # format
cargo clippy -- -D warnings  # lint (deny all warnings)
cargo test                   # test
cargo audit                  # security scan (cargo-audit)
cargo tarpaulin              # coverage
```

---

# C++ AI Rules

> Full reference: `cpp/style-guide.md`

---

## Formatting (Google C++ Style)

- Line limit: **80 chars**
- Indentation: **2 spaces**
- Access specifiers indented 1 space: ` public:`, ` private:`
- File extensions: `.cc` source, `.h` header
- Use `#pragma once` for include guards

## Naming

| Concept | Style | Example |
|---------|-------|---------|
| Types (class/struct/enum) | `PascalCase` | `OrderService`, `PaymentResult` |
| Functions | `CamelCase()` | `ProcessOrder()`, `GetTotal()` |
| Variables | `snake_case` | `order_id`, `total_price` |
| Member variables | `snake_case_` (trailing `_`) | `order_id_`, `total_` |
| Constants | `kCamelCase` | `kMaxRetries`, `kDefaultTimeout` |
| Namespaces | `snake_case` | `myapp::orders` |

## Memory Management (C++ Core Guidelines)

```cpp
// ✅ GOOD: smart pointers — never raw new/delete
auto service = std::make_unique<OrderService>(repo.get());
auto config = std::make_shared<AppConfig>(configPath);

// ❌ NEVER in application code
Order* order = new Order(id, total);  // manual memory = leaks
delete order;

// ✅ RAII: resources owned by objects
std::ifstream file(path);  // closes automatically
```

## Error Handling

```cpp
// C++23 std::expected (no exceptions policy)
[[nodiscard]] std::expected<Order, std::error_code> FindOrder(const std::string& id);

// Use [[nodiscard]] on functions returning error codes
[[nodiscard]] absl::Status ValidateOrder(const Order& order);
```

## Unsafe Code

```cpp
// Every unsafe block requires a SAFETY comment
// SAFETY: We have exclusive access via Box::into_raw() and pointer has not been aliased.
auto value = unsafe_operation(ptr);
```

## Security

```cpp
// ❌ FORBIDDEN: buffer-overflow risk
scanf("%s", buffer);
gets(buffer);

// ✅ SAFE: bounds-checked
std::string input;
std::cin >> input;

// ✅ Array bounds: use .at() in debug builds
vec.at(index);  // throws out_of_range if invalid
```

## Tooling

```bash
clang-format -i **/*.cc **/*.h  # format
clang-tidy **/*.cc               # lint
cmake --build . --target test    # test
```

---

# SQL AI Rules

> Full reference: `sql/style-guide.md`

---

## Formatting

- Keywords: **UPPERCASE** (`SELECT`, `FROM`, `WHERE`, `JOIN`)
- Indentation: **4 spaces** per level
- Each clause on its own line
- Always use `AS` for aliases
- Explicit `INNER JOIN`, `LEFT JOIN` — avoid implicit joins (comma in FROM)

## Naming (dbt Style)

| Object | Style | Example |
|--------|-------|---------|
| Tables | `snake_case`, **plural** | `users`, `order_items` |
| Columns | `snake_case` | `user_id`, `total_price` |
| Booleans | `is_`, `has_`, `can_` prefix | `is_active`, `has_subscription` |
| Timestamps | `_at` suffix | `created_at`, `updated_at`, `deleted_at` |
| Indexes | `idx_<table>_<columns>` | `idx_orders_user_id` |
| FK constraints | `fk_<table>_<referenced>` | `fk_orders_users` |

## Query Patterns

```sql
-- ✅ GOOD: explicit columns, CTEs, parameterized
WITH active_orders AS (
    SELECT
        o.id,
        o.user_id,
        o.total,
        o.status
    FROM orders AS o
    WHERE o.is_deleted = FALSE
        AND o.status = $1
)
SELECT *
FROM active_orders
ORDER BY created_at DESC
LIMIT $2;

-- ❌ BAD
select * from orders where status = 'pending';  -- lowercase, wildcard, literal
```

## Safety Rules

```sql
-- ❌ CRITICAL: SQL injection
SELECT * FROM users WHERE email = '" + email + "'";

-- ✅ ALWAYS parameterize
SELECT * FROM users WHERE email = $1;  -- PostgreSQL
SELECT * FROM users WHERE email = ?;   -- MySQL

-- ✅ IS NULL / IS NOT NULL (never = NULL)
WHERE deleted_at IS NULL
```

## Schema Standards

- Primary keys: `UUID` or `BIGINT` — not `INT` (exhausts quickly)
- Timestamps: `TIMESTAMPTZ` (never naive `TIMESTAMP`)
- Money: `NUMERIC(12,2)` or integer cents — **never** `FLOAT`
- Every table: `id`, `created_at`, `updated_at` minimum

## Performance

- Index all columns in `WHERE`, `JOIN ON`, `ORDER BY`
- Use `CREATE INDEX CONCURRENTLY` (PostgreSQL) — non-blocking
- `EXPLAIN ANALYZE` before releasing queries on tables > 100k rows
- Avoid `SELECT *` — specify columns explicitly
- Use keyset pagination over `OFFSET` for large datasets

---

# Bash AI Rules

> Full reference: `bash/style-guide.md`

---

## Required Boilerplate

Every bash script MUST begin with:

```bash
#!/usr/bin/env bash
set -euo pipefail
# -e: exit on error
# -u: error on unset variables
# -o pipefail: pipe failures are caught
```

## Formatting (shfmt)

- Indentation: **2 spaces**
- Line limit: **80 chars** (soft)

## Naming

| Concept | Style | Example |
|---------|-------|---------|
| Functions | `snake_case` | `deploy_to_env`, `get_config_value` |
| Local variables | `snake_case` | `user_id`, `output_file` |
| Global constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEPLOY_TIMEOUT` |
| Environment vars | `UPPER_SNAKE_CASE` | `DATABASE_URL`, `API_KEY` |

## Always Quote Variables

```bash
# ✅ ALWAYS quote
cp "${source_file}" "${dest_dir}"
if [[ "${name}" == "alice" ]]; then

# ❌ NEVER unquoted (word splitting / globbing)
cp $source_file $dest_dir
if [ $name = "alice" ]; then
```

## Conditionals

```bash
# ✅ [[ ]] in bash (not [ ])
if [[ "${count}" -gt 0 && "${status}" == "active" ]]; then

# ✅ $() not backticks
result="$(some_command "${arg}")"
```

## Functions

```bash
# ✅ local variables, validate args, errors to stderr
deploy() {
  local environment="${1:?Usage: deploy <environment>}"
  local version="${2:?Usage: deploy <environment> <version>}"

  if [[ ! "${environment}" =~ ^(staging|production)$ ]]; then
    echo "ERROR: Invalid environment: ${environment}" >&2
    return 1
  fi
  # ...
}
```

## Security

```bash
# ❌ NEVER eval user input — arbitrary code execution
eval "${user_input}"

# ✅ Whitelist validation
case "${env}" in
  staging|production) deploy "${env}" ;;
  *) echo "ERROR: Invalid environment" >&2; exit 1 ;;
esac

# ✅ Temp files with mktemp + trap cleanup
tmp="$(mktemp)"
trap 'rm -f "${tmp}"' EXIT

# ✅ Secrets from environment, never hardcoded
API_KEY="${API_KEY:?API_KEY must be set}"
```

## Tooling

```bash
shellcheck myscript.sh        # lint (mandatory, runs in CI)
shfmt -i 2 -w myscript.sh    # format
bats tests/                   # test
```

---

