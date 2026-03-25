# Go Style Guide

> **Sources:** Effective Go (golang.org/doc/effective_go), Google Go Style Guide (google.github.io/styleguide/go), Uber Go Style Guide (github.com/uber-go/guide/blob/master/style.md)

---

## A. Formatting & Style

**Use `gofmt` or `goimports` for all formatting.** Go formatting is not a debate — `gofmt` is the standard.

### Line Length

No official hard limit. `gofmt` does not enforce line length. However:
- **Keep lines under 100 characters** as a soft target (Google Go Style Guide)
- Long lines are acceptable if they are a single expression that can't logically be split

### Indentation

**Tabs** — enforced by `gofmt`. Never use spaces for indentation in Go.

### Import Grouping (Effective Go, Google Go Style)

```go
import (
    // Standard library
    "context"
    "fmt"
    "time"

    // External packages (blank line)
    "github.com/jackc/pgx/v5/pgxpool"
    "go.uber.org/zap"

    // Internal packages (blank line)
    "github.com/mycompany/myapp/internal/domain"
    "github.com/mycompany/myapp/internal/infrastructure"
)
```

- `goimports` manages this automatically

---

## B. Naming Conventions (Effective Go §Names)

| Concept | Convention | Example |
|---------|-----------|---------|
| Exported (public) | `PascalCase` | `OrderService`, `ProcessPayment` |
| Unexported (private) | `camelCase` | `orderRepo`, `processPayment` |
| Packages | `lowercase` (no underscores) | `orders`, `payment`, `httputil` |
| Interfaces (1 method) | Method name + `er` | `Reader`, `Writer`, `Stringer` |
| Interfaces (multi-method) | Descriptive noun | `OrderRepository`, `PaymentGateway` |
| Constants | `PascalCase` (exported) or `camelCase` (unexported) | `MaxRetries`, `defaultTimeout` |
| Error variables | `Err` prefix | `ErrOrderNotFound`, `ErrPaymentDeclined` |
| Error types | `Error` suffix | `OrderNotFoundError`, `ValidationError` |

### Keep Names Short in Context (Effective Go)

```go
// ❌ BAD: redundant context in variable name
func (s *OrderService) GetOrder(orderID string) (*Order, error) {
    foundOrder := s.orderRepository.FindByOrderID(orderID) // "Order" repeated
    return foundOrder, nil
}

// ✅ GOOD: context is already clear from function/receiver
func (s *OrderService) Get(id string) (*Order, error) {
    return s.repo.FindByID(id)
}
```

### Acronyms

All letters of an acronym have the same case:

```go
// ✅ GOOD
userID, orderURL, httpClient, parseJSON, ServeHTTP

// ❌ BAD
userId, orderUrl, httpClient, parseJson, ServeHttp
```

---

## C. Functions & Methods

### Error as Last Return Value

```go
// ✅ GOOD: error is always the last return value
func (r *PostgresOrderRepo) FindByID(ctx context.Context, id string) (*Order, error) {
    ...
}

// ❌ BAD: error not last
func FindOrder(id string) (error, *Order) { ... }
```

### Accept Interfaces, Return Structs (Uber Go Style)

```go
// ✅ GOOD: accept interface (for testability), return concrete type
func NewOrderService(repo OrderRepository, gateway PaymentGateway) *OrderService {
    return &OrderService{repo: repo, gateway: gateway}
}

// ❌ BAD: returning an interface — forces caller to deal with interface assertion
func NewOrderService(repo OrderRepository) OrderServiceInterface { ... }
```

### Keep Functions Short

Maximum ~40 lines per function. If longer, extract helpers.

### Early Returns for Error Handling

```go
// ✅ GOOD: error handling at each step, no nesting
func (s *OrderService) ProcessPayment(ctx context.Context, orderID, cardToken string) (*PaymentConfirmation, error) {
    order, err := s.repo.FindByID(ctx, orderID)
    if err != nil {
        return nil, fmt.Errorf("finding order: %w", err)
    }
    if order == nil {
        return nil, ErrOrderNotFound
    }
    if order.Status != StatusPending {
        return nil, fmt.Errorf("order %s is not payable (status: %s): %w", orderID, order.Status, ErrOrderNotPayable)
    }

    payment, err := s.gateway.Charge(ctx, order.Total, cardToken)
    if err != nil {
        return nil, fmt.Errorf("charging payment: %w", err)
    }

    return &PaymentConfirmation{PaymentID: payment.ID, OrderID: orderID}, nil
}
```

---

## D. Comments & Documentation

### GoDoc Comments

```go
// ProcessPayment processes a payment for an existing pending order.
//
// It validates the order status, charges the payment gateway, and
// updates the order to Paid status. The context is used for cancellation
// and deadline propagation to all downstream calls.
//
// Returns ErrOrderNotFound if the order does not exist.
// Returns ErrOrderNotPayable if the order is not in Pending status.
func (s *OrderService) ProcessPayment(ctx context.Context, orderID, cardToken string) (*PaymentConfirmation, error) {
```

**Rules:**
- Every exported function, type, variable, and constant needs a GoDoc comment
- Comment starts with the name of the thing being documented: `// ProcessPayment ...`
- Package-level comment: `// Package orders provides ...`

---

## E. Error Handling (See also error-handling.md)

### Always Handle Errors Explicitly

```go
// ❌ BAD: ignoring error with _
result, _ := repo.FindByID(ctx, id)

// ❌ BAD: checking error inside if, not handling it
if err := repo.Save(ctx, order); err == nil {
    // ...
}

// ✅ GOOD: explicit error check and handling
result, err := repo.FindByID(ctx, id)
if err != nil {
    return fmt.Errorf("finding order %s: %w", id, err)
}
```

### Error Wrapping with `%w`

```go
// ✅ GOOD: wrap with %w to preserve error chain for errors.Is/errors.As
if err := db.QueryRow(ctx, query, id).Scan(&order); err != nil {
    return fmt.Errorf("querying order %s: %w", id, err)
}

// Caller can unwrap:
if errors.Is(err, pgx.ErrNoRows) {
    return ErrOrderNotFound
}
```

---

## F. Interfaces & Design

### Interface Size (Effective Go)

Prefer small interfaces. The most useful interfaces in the Go standard library are `io.Reader`, `io.Writer`, `io.Closer` — all single-method.

```go
// ✅ GOOD: minimal, focused interfaces
type OrderReader interface {
    FindByID(ctx context.Context, id string) (*Order, error)
}

type OrderWriter interface {
    Save(ctx context.Context, order *Order) error
}

type OrderRepository interface {
    OrderReader
    OrderWriter
}
```

### Avoid Embedding in Public Interfaces (Uber Go Style)

```go
// ❌ BAD: embedding causes all methods to become part of the interface surface
type Service interface {
    http.Handler // now everything that implements Service must also implement ServeHTTP
}

// ✅ GOOD: explicit methods
type Service interface {
    ProcessOrder(ctx context.Context, req ProcessOrderRequest) (*Order, error)
}
```

---

## G. Security

```go
// SQL injection — use pgx parameterized queries
// ❌ BAD
query := "SELECT * FROM users WHERE email = '" + email + "'"

// ✅ GOOD: pgx parameterized
var user User
err := pool.QueryRow(ctx,
    "SELECT id, email, name FROM users WHERE email = $1",
    email,
).Scan(&user.ID, &user.Email, &user.Name)

// Secrets from environment
dbURL := os.Getenv("DATABASE_URL")
if dbURL == "" {
    log.Fatal("DATABASE_URL environment variable is required")
}
```
