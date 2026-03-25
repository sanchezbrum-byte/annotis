// test_example.cpp — unit tests for good_service.cpp using Google Test.
//
// Build: g++ -std=c++17 good_service.cpp test_example.cpp -lgtest -lgtest_main -o test_service
//         ./test_service

#include "good_service.cpp"  // Include for unit testing; in a real project use a header.

#include <gtest/gtest.h>
#include <memory>
#include <optional>

using namespace orders;

// ---------------------------------------------------------------------------
// Fake implementations
// ---------------------------------------------------------------------------

class FakeOrderRepository : public OrderRepository {
public:
    std::unordered_map<std::string, Order> store;
    std::vector<Order> saved;

    std::optional<Order> FindById(const OrderId& id) const override {
        auto it = store.find(id.value);
        if (it == store.end()) return std::nullopt;
        return it->second;
    }

    bool Save(const Order& order) override {
        saved.push_back(order);
        store[order.id.value] = order;
        return true;
    }
};

class StubPaymentGateway : public PaymentGateway {
public:
    PaymentResult response;

    explicit StubPaymentGateway(PaymentResult r) : response(std::move(r)) {}

    PaymentResult Charge(int64_t, std::string_view, std::string_view) override {
        return response;
    }
};

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

Order MakePendingOrder(std::string id = "order-123") {
    return Order{
        .id         = OrderId{std::move(id)},
        .user_id    = "user-456",
        .total_cents = 10'000,
        .currency   = "USD",
        .status     = OrderStatus::kPending,
    };
}

std::shared_ptr<FakeOrderRepository> RepoWithOrder(Order order) {
    auto repo = std::make_shared<FakeOrderRepository>();
    repo->store[order.id.value] = std::move(order);
    return repo;
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

TEST(OrderPaymentService, ValidCard_ReturnsPaymentId) {
    // Arrange
    auto order = MakePendingOrder();
    auto repo  = RepoWithOrder(order);
    auto gw    = std::make_shared<StubPaymentGateway>(PaymentResult{std::string{"pay-789"}});
    OrderPaymentService svc{repo, gw};

    // Act
    auto result = svc.ProcessPayment(order.id, "tok_visa");

    // Assert
    ASSERT_TRUE(std::holds_alternative<std::string>(result));
    EXPECT_EQ(std::get<std::string>(result), "pay-789");
    ASSERT_EQ(repo->saved.size(), 1u);
    EXPECT_EQ(repo->saved[0].status, OrderStatus::kPaid);
}

TEST(OrderPaymentService, OrderNotFound_ReturnsNotFoundError) {
    auto repo = std::make_shared<FakeOrderRepository>(); // empty
    auto gw   = std::make_shared<StubPaymentGateway>(PaymentResult{std::string{"pay-1"}});
    OrderPaymentService svc{repo, gw};

    auto result = svc.ProcessPayment(OrderId{"missing"}, "tok_visa");

    ASSERT_TRUE(std::holds_alternative<PaymentError>(result));
    EXPECT_TRUE(std::holds_alternative<NotFound>(std::get<PaymentError>(result)));
}

TEST(OrderPaymentService, AlreadyPaid_ReturnsNotPayableError) {
    auto order = MakePendingOrder();
    order.status = OrderStatus::kPaid;
    auto repo = RepoWithOrder(order);
    auto gw   = std::make_shared<StubPaymentGateway>(PaymentResult{std::string{"pay-1"}});
    OrderPaymentService svc{repo, gw};

    auto result = svc.ProcessPayment(order.id, "tok_visa");

    ASSERT_TRUE(std::holds_alternative<PaymentError>(result));
    EXPECT_TRUE(std::holds_alternative<NotPayable>(std::get<PaymentError>(result)));
}

TEST(OrderPaymentService, CardDeclined_ReturnsCardDeclinedAndDoesNotSave) {
    auto order = MakePendingOrder();
    auto repo  = RepoWithOrder(order);
    auto gw    = std::make_shared<StubPaymentGateway>(
        PaymentResult{PaymentError{CardDeclined{"insufficient_funds"}}});
    OrderPaymentService svc{repo, gw};

    auto result = svc.ProcessPayment(order.id, "tok_declined");

    ASSERT_TRUE(std::holds_alternative<PaymentError>(result));
    EXPECT_TRUE(std::holds_alternative<CardDeclined>(std::get<PaymentError>(result)));
    // ✅ Data integrity: nothing saved when payment fails
    EXPECT_TRUE(repo->saved.empty());
}

TEST(OrderPaymentService, EmptyCardToken_ReturnsServiceError) {
    auto order = MakePendingOrder();
    auto repo  = RepoWithOrder(order);
    auto gw    = std::make_shared<StubPaymentGateway>(PaymentResult{std::string{"pay-1"}});
    OrderPaymentService svc{repo, gw};

    auto result = svc.ProcessPayment(order.id, "");

    ASSERT_TRUE(std::holds_alternative<PaymentError>(result));
    EXPECT_TRUE(std::holds_alternative<ServiceError>(std::get<PaymentError>(result)));
}

TEST(OrderPaymentService, NullDependency_ThrowsInvalidArgument) {
    EXPECT_THROW(
        OrderPaymentService(nullptr, std::make_shared<StubPaymentGateway>(
            PaymentResult{std::string{"x"}})),
        std::invalid_argument);
}
