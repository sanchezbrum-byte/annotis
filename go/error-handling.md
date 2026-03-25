# Go Error Handling

---

## Sentinel Errors and Error Types

```go
// Sentinel errors — for simple, expected errors
var (
    ErrOrderNotFound   = errors.New("order not found")
    ErrOrderNotPayable = errors.New("order is not in payable status")
    ErrPaymentDeclined = errors.New("payment declined")
)

// Structured error types — when errors need context
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed on field %q: %s", e.Field, e.Message)
}

// Error with cause (wraps another error)
type PaymentGatewayError struct {
    Code    string
    Message string
    Cause   error
}

func (e *PaymentGatewayError) Error() string {
    return fmt.Sprintf("payment gateway error %s: %s", e.Code, e.Message)
}

func (e *PaymentGatewayError) Unwrap() error {
    return e.Cause // enables errors.Is/errors.As on wrapped error
}
```

## Checking Error Types

```go
// errors.Is — checks for sentinel or wrapped sentinel
if errors.Is(err, ErrOrderNotFound) {
    http.Error(w, "Order not found", http.StatusNotFound)
    return
}

// errors.As — extracts structured error
var validationErr *ValidationError
if errors.As(err, &validationErr) {
    http.Error(w, validationErr.Error(), http.StatusBadRequest)
    return
}
```

## Error Wrapping Strategy

```go
// Wrap errors with context at each layer
func (r *PostgresOrderRepo) FindByID(ctx context.Context, id string) (*Order, error) {
    var order Order
    err := r.pool.QueryRow(ctx, "SELECT ... FROM orders WHERE id = $1", id).
        Scan(&order.ID, &order.Status /* ... */)
    if err != nil {
        if errors.Is(err, pgx.ErrNoRows) {
            return nil, ErrOrderNotFound // convert infrastructure error to domain error
        }
        return nil, fmt.Errorf("postgres FindByID(%s): %w", id, err)
    }
    return &order, nil
}
```
