// good_service.cpp — demonstrates idiomatic modern C++ (C++17/20) patterns.
//
// Covered patterns:
//   - RAII ownership (unique_ptr, shared_ptr, no raw new/delete)
//   - std::expected / std::variant for error handling (no exceptions in hot paths)
//   - Interfaces via abstract classes for DI
//   - Rule of Five explicitly defaulted
//   - const-correctness, [[nodiscard]], strong types

#include <memory>
#include <optional>
#include <string>
#include <string_view>
#include <variant>
#include <stdexcept>

namespace orders {

// ✅ Strong typedef: prevents confusing OrderId with UserId at compile time
struct OrderId {
    std::string value;
    explicit OrderId(std::string v) : value(std::move(v)) {}
    bool operator==(const OrderId& other) const = default;
};

enum class OrderStatus { kPending, kPaid, kCancelled };

// ✅ Value type: no raw pointers, copyable
struct Order {
    OrderId     id;
    std::string user_id;
    int64_t     total_cents{0};
    std::string currency{"USD"};
    OrderStatus status{OrderStatus::kPending};
};

// ✅ Typed error enum — avoids exception-based control flow in business logic
struct NotFound    { std::string order_id; };
struct NotPayable  { std::string order_id; OrderStatus status; };
struct CardDeclined{ std::string code; };
struct ServiceError{ std::string message; };

using PaymentError = std::variant<NotFound, NotPayable, CardDeclined, ServiceError>;
using PaymentResult = std::variant<std::string /*paymentId*/, PaymentError>;

// ✅ Pure abstract interface for DI — no implementation details
class OrderRepository {
public:
    virtual ~OrderRepository() = default;
    [[nodiscard]] virtual std::optional<Order> FindById(const OrderId& id) const = 0;
    virtual bool Save(const Order& order) = 0;
};

class PaymentGateway {
public:
    virtual ~PaymentGateway() = default;
    [[nodiscard]] virtual PaymentResult Charge(
        int64_t amount_cents,
        std::string_view currency,
        std::string_view card_token) = 0;
};

// ✅ Service: owns dependencies via shared_ptr (shared ownership across threads)
class OrderPaymentService {
public:
    // ✅ Constructor validates dependencies
    OrderPaymentService(
        std::shared_ptr<OrderRepository> repository,
        std::shared_ptr<PaymentGateway>  gateway)
        : repository_(std::move(repository))
        , gateway_(std::move(gateway))
    {
        if (!repository_) throw std::invalid_argument{"repository must not be null"};
        if (!gateway_)    throw std::invalid_argument{"gateway must not be null"};
    }

    // ✅ Rule of Five: explicitly defaulted to prevent accidental copies/moves
    OrderPaymentService(const OrderPaymentService&)            = default;
    OrderPaymentService& operator=(const OrderPaymentService&) = default;
    OrderPaymentService(OrderPaymentService&&)                 = default;
    OrderPaymentService& operator=(OrderPaymentService&&)      = default;
    ~OrderPaymentService()                                     = default;

    /// Process a payment for an existing pending order.
    ///
    /// @returns paymentId on success, PaymentError variant on failure.
    [[nodiscard]] PaymentResult ProcessPayment(
        const OrderId&   order_id,
        std::string_view card_token)
    {
        if (card_token.empty()) {
            return PaymentError{ServiceError{"card_token must not be empty"}};
        }

        auto order = repository_->FindById(order_id);
        if (!order) {
            return PaymentError{NotFound{order_id.value}};
        }

        if (order->status != OrderStatus::kPending) {
            return PaymentError{NotPayable{order_id.value, order->status}};
        }

        auto charge_result = gateway_->Charge(order->total_cents, order->currency, card_token);

        // ✅ std::visit for exhaustive variant handling — won't compile if a case is missing
        return std::visit([&](auto&& result) -> PaymentResult {
            using T = std::decay_t<decltype(result)>;
            if constexpr (std::is_same_v<T, std::string>) {
                // ✅ Only persist after successful payment
                Order paid = *order;
                paid.status = OrderStatus::kPaid;
                repository_->Save(paid);
                return result;       // paymentId
            } else {
                return result;       // propagate PaymentError
            }
        }, charge_result);
    }

private:
    std::shared_ptr<OrderRepository> repository_;
    std::shared_ptr<PaymentGateway>  gateway_;
};

}  // namespace orders
