package orders_test

import (
	"context"
	"errors"
	"log/slog"
	"os"
	"testing"
	"time"

	orders "github.com/example/myapp/orders/examples"
)

// ---------------------------------------------------------------------------
// Fake implementations (preferred over mocks when simple)
// ---------------------------------------------------------------------------

type fakeOrderRepo struct {
	store map[string]*orders.Order
}

func newFakeOrderRepo() *fakeOrderRepo {
	return &fakeOrderRepo{store: make(map[string]*orders.Order)}
}

func (r *fakeOrderRepo) FindByID(_ context.Context, id string) (*orders.Order, error) {
	o, ok := r.store[id]
	if !ok {
		return nil, nil // not found = nil, nil (idiomatic Go)
	}
	return o, nil
}

func (r *fakeOrderRepo) Save(_ context.Context, order *orders.Order) error {
	r.store[order.ID] = order
	return nil
}

type fakePaymentGateway struct {
	paymentID string
	err       error
}

func (g *fakePaymentGateway) Charge(_ context.Context, _, _, _ string) (string, error) {
	return g.paymentID, g.err
}

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

func buildService(repo *fakeOrderRepo, gateway *fakePaymentGateway) *orders.Service {
	logger := slog.New(slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{Level: slog.LevelError}))
	return orders.NewService(repo, gateway, logger)
}

func buildPendingOrder() *orders.Order {
	return &orders.Order{
		ID:        "order-123",
		UserID:    "user-456",
		Total:     100.00,
		Currency:  "USD",
		Status:    orders.StatusPending,
		CreatedAt: time.Now(),
	}
}

// ---------------------------------------------------------------------------
// Table-driven tests
// ---------------------------------------------------------------------------

// TestService_ProcessPayment_ValidCard tests the happy path with a valid card.
func TestService_ProcessPayment_ValidCard_ReturnsConfirmation(t *testing.T) {
	t.Parallel()

	// Arrange
	repo := newFakeOrderRepo()
	order := buildPendingOrder()
	repo.store[order.ID] = order

	gateway := &fakePaymentGateway{paymentID: "pay-789"}
	svc := buildService(repo, gateway)

	// Act
	confirmation, err := svc.ProcessPayment(context.Background(), order.ID, "tok_visa")

	// Assert
	if err != nil {
		t.Fatalf("expected no error, got: %v", err)
	}
	if confirmation.PaymentID != "pay-789" {
		t.Errorf("PaymentID = %q, want %q", confirmation.PaymentID, "pay-789")
	}
	if confirmation.OrderID != order.ID {
		t.Errorf("OrderID = %q, want %q", confirmation.OrderID, order.ID)
	}
}

func TestService_ProcessPayment_OrderNotFound_ReturnsErrOrderNotFound(t *testing.T) {
	t.Parallel()

	svc := buildService(newFakeOrderRepo(), &fakePaymentGateway{paymentID: "pay-1"})

	_, err := svc.ProcessPayment(context.Background(), "nonexistent-id", "tok_visa")

	if !errors.Is(err, orders.ErrOrderNotFound) {
		t.Errorf("expected ErrOrderNotFound, got: %v", err)
	}
}

func TestService_ProcessPayment_AlreadyPaid_ReturnsErrOrderNotPayable(t *testing.T) {
	t.Parallel()

	repo := newFakeOrderRepo()
	paidOrder := buildPendingOrder()
	paidOrder.Status = orders.StatusPaid
	repo.store[paidOrder.ID] = paidOrder

	svc := buildService(repo, &fakePaymentGateway{paymentID: "pay-1"})

	_, err := svc.ProcessPayment(context.Background(), paidOrder.ID, "tok_visa")

	if !errors.Is(err, orders.ErrOrderNotPayable) {
		t.Errorf("expected ErrOrderNotPayable, got: %v", err)
	}
}

func TestService_ProcessPayment_GatewayDeclines_ReturnsErrPaymentDeclined(t *testing.T) {
	t.Parallel()

	repo := newFakeOrderRepo()
	repo.store["order-123"] = buildPendingOrder()

	gateway := &fakePaymentGateway{err: orders.ErrPaymentDeclined}
	svc := buildService(repo, gateway)

	_, err := svc.ProcessPayment(context.Background(), "order-123", "tok_declined")

	if !errors.Is(err, orders.ErrPaymentDeclined) {
		t.Errorf("expected ErrPaymentDeclined, got: %v", err)
	}
}

// TestService_ProcessPayment_Validation covers corner cases for invalid input.
func TestService_ProcessPayment_Validation(t *testing.T) {
	t.Parallel()

	svc := buildService(newFakeOrderRepo(), &fakePaymentGateway{})
	ctx := context.Background()

	tests := []struct {
		name      string
		orderID   string
		cardToken string
	}{
		{"empty orderID", "", "tok_visa"},
		{"empty cardToken", "order-1", ""},
		{"both empty", "", ""},
	}

	for _, tt := range tests {
		tt := tt // capture range variable
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			_, err := svc.ProcessPayment(ctx, tt.orderID, tt.cardToken)
			if err == nil {
				t.Error("expected error, got nil")
			}
		})
	}
}

// TestService_ProcessPayment_GatewayFail_DoesNotSaveOrder verifies data integrity:
// order status is not saved when payment fails.
func TestService_ProcessPayment_GatewayFail_DoesNotSaveOrder(t *testing.T) {
	t.Parallel()

	repo := newFakeOrderRepo()
	order := buildPendingOrder()
	repo.store[order.ID] = order

	gateway := &fakePaymentGateway{err: errors.New("connection refused")}
	svc := buildService(repo, gateway)

	_, _ = svc.ProcessPayment(context.Background(), order.ID, "tok_visa")

	// Verify the order status was not changed
	saved := repo.store[order.ID]
	if saved.Status != orders.StatusPending {
		t.Errorf("order status = %q after failed payment; want %q", saved.Status, orders.StatusPending)
	}
}
