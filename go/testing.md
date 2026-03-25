# Go Testing Standards

---

## Table-Driven Tests (Idiomatic Go)

```go
func TestCalculateTotal(t *testing.T) {
    t.Parallel() // ✅ Run tests in parallel when they have no shared state

    tests := []struct {
        name     string
        items    []OrderItem
        expected decimal.Decimal
    }{
        {
            name:     "empty items returns zero",
            items:    []OrderItem{},
            expected: decimal.Zero,
        },
        {
            name: "single item returns item price",
            items: []OrderItem{
                {UnitPrice: decimal.NewFromFloat(100.00), Quantity: 1},
            },
            expected: decimal.NewFromFloat(100.00),
        },
        {
            name: "multiple items returns sum",
            items: []OrderItem{
                {UnitPrice: decimal.NewFromFloat(25.00), Quantity: 2},
                {UnitPrice: decimal.NewFromFloat(50.00), Quantity: 1},
            },
            expected: decimal.NewFromFloat(100.00),
        },
    }

    for _, tt := range tests {
        tt := tt // capture range variable (pre-Go 1.22)
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()
            got := CalculateTotal(tt.items)
            if !got.Equal(tt.expected) {
                t.Errorf("CalculateTotal(%v) = %v, want %v", tt.items, got, tt.expected)
            }
        })
    }
}
```

## Test Naming

```go
// Package-level tests
func TestOrderService_ProcessPayment_WithValidCard_ReturnsConfirmation(t *testing.T) {}
func TestOrderService_ProcessPayment_WhenOrderNotFound_ReturnsErrOrderNotFound(t *testing.T) {}
```

## Using testify

```go
import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestProcessPayment(t *testing.T) {
    // require.* stops test on failure; assert.* continues
    order, err := repo.FindByID(ctx, "order-1")
    require.NoError(t, err)                // fatal if err != nil
    require.NotNil(t, order)               // fatal if order == nil

    assert.Equal(t, StatusPending, order.Status)
    assert.Equal(t, "USD", order.Currency)
}
```

## Integration Tests with testcontainers-go

```go
func TestOrderRepository_Integration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test in short mode")
    }

    ctx := context.Background()
    pgContainer, err := postgres.RunContainer(ctx,
        testcontainers.WithImage("postgres:16"),
        postgres.WithDatabase("testdb"),
    )
    require.NoError(t, err)
    t.Cleanup(func() { pgContainer.Terminate(ctx) })

    connStr, _ := pgContainer.ConnectionString(ctx, "sslmode=disable")
    repo := NewPostgresOrderRepo(connStr)

    // Test
    order := NewOrder("order-1", "user-1")
    err = repo.Save(ctx, order)
    require.NoError(t, err)

    found, err := repo.FindByID(ctx, "order-1")
    require.NoError(t, err)
    assert.Equal(t, order.ID, found.ID)
}
```

## golangci-lint Configuration

```yaml
# .golangci.yml
linters:
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused
    - gocritic
    - gocyclo
    - revive
    - gosec
    - noctx

linters-settings:
  gocyclo:
    min-complexity: 15
  gosec:
    severity: medium
```
