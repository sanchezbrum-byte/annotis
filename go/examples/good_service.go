// Package orders implements the order management use cases.
// It follows Clean Architecture: this package contains only application logic,
// no HTTP or database concerns.
package orders

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"time"
)

// Sentinel errors — callers can check with errors.Is
var (
	ErrOrderNotFound   = errors.New("order not found")
	ErrOrderNotPayable = errors.New("order is not in payable status")
	ErrPaymentDeclined = errors.New("payment declined")
)

// OrderStatus represents the lifecycle state of an order.
type OrderStatus string

const (
	StatusPending   OrderStatus = "pending"
	StatusPaid      OrderStatus = "paid"
	StatusCancelled OrderStatus = "cancelled"
)

// Order is the core domain entity.
type Order struct {
	ID        string
	UserID    string
	Total     float64
	Currency  string
	Status    OrderStatus
	CreatedAt time.Time
}

// PaymentConfirmation is the result of a successful payment.
type PaymentConfirmation struct {
	PaymentID string
	OrderID   string
	Amount    float64
}

// OrderRepository defines the persistence port (interface).
// Accept interfaces, return concrete types (Uber Go Style).
type OrderRepository interface {
	FindByID(ctx context.Context, id string) (*Order, error)
	Save(ctx context.Context, order *Order) error
}

// PaymentGateway defines the payment processing port.
type PaymentGateway interface {
	Charge(ctx context.Context, amount float64, currency, cardToken string) (string, error)
}

// Service handles order-related use cases.
// It depends only on interfaces — never on concrete infrastructure types.
type Service struct {
	repo    OrderRepository
	gateway PaymentGateway
	logger  *slog.Logger
}

// NewService creates a new order Service with injected dependencies.
// Returns a concrete type, not an interface (Uber Go Style).
func NewService(repo OrderRepository, gateway PaymentGateway, logger *slog.Logger) *Service {
	return &Service{
		repo:    repo,
		gateway: gateway,
		logger:  logger,
	}
}

// ProcessPayment processes a payment for an existing pending order.
//
// Validates the order state, charges the payment gateway, and persists
// the status change. Uses context for cancellation and deadline propagation.
//
// Returns ErrOrderNotFound if the order does not exist.
// Returns ErrOrderNotPayable if the order is not in pending status.
// Returns ErrPaymentDeclined if the gateway declines the card.
func (s *Service) ProcessPayment(ctx context.Context, orderID, cardToken string) (*PaymentConfirmation, error) {
	// ✅ Early validation before any side effects
	if orderID == "" {
		return nil, errors.New("orderID is required")
	}
	if cardToken == "" {
		return nil, errors.New("cardToken is required")
	}

	// ✅ Load and validate order state
	order, err := s.repo.FindByID(ctx, orderID)
	if err != nil {
		return nil, fmt.Errorf("finding order %s: %w", orderID, err)
	}
	if order == nil {
		return nil, ErrOrderNotFound
	}
	if order.Status != StatusPending {
		return nil, fmt.Errorf("order %s has status %q: %w", orderID, order.Status, ErrOrderNotPayable)
	}

	s.logger.InfoContext(ctx, "processing payment",
		slog.String("order_id", orderID),
		slog.Float64("amount", order.Total),
		slog.String("currency", order.Currency),
	)

	// ✅ Charge the gateway — translate infrastructure errors to domain errors
	paymentID, err := s.gateway.Charge(ctx, order.Total, order.Currency, cardToken)
	if err != nil {
		// Check if it's a decline (domain error) vs. service unavailable (infra error)
		if errors.Is(err, ErrPaymentDeclined) {
			s.logger.InfoContext(ctx, "payment declined", slog.String("order_id", orderID))
			return nil, ErrPaymentDeclined
		}
		s.logger.ErrorContext(ctx, "payment gateway error",
			slog.String("order_id", orderID),
			slog.String("error", err.Error()),
		)
		return nil, fmt.Errorf("charging payment for order %s: %w", orderID, err)
	}

	// ✅ Update order status — only after payment succeeds
	order.Status = StatusPaid
	if err := s.repo.Save(ctx, order); err != nil {
		// Payment succeeded but save failed — log for manual reconciliation
		s.logger.ErrorContext(ctx, "CRITICAL: payment succeeded but order save failed — requires manual reconciliation",
			slog.String("order_id", orderID),
			slog.String("payment_id", paymentID),
			slog.String("error", err.Error()),
		)
		return nil, fmt.Errorf("saving order %s after payment: %w", orderID, err)
	}

	s.logger.InfoContext(ctx, "payment processed",
		slog.String("order_id", orderID),
		slog.String("payment_id", paymentID),
	)

	return &PaymentConfirmation{
		PaymentID: paymentID,
		OrderID:   orderID,
		Amount:    order.Total,
	}, nil
}
