# C++ Testing Standards

> **Tools:** Google Test (gtest), Google Mock (gmock), Catch2

---

## Google Test Conventions

```cpp
// test/order_service_test.cc
#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "src/order_service.h"

using ::testing::Return;
using ::testing::NiceMock;
using ::testing::_;

// Mock for dependency
class MockPaymentGateway : public PaymentGateway {
 public:
  MOCK_METHOD(PaymentResult, Charge,
    (double amount, const std::string& token), (override));
};

// Test fixture
class OrderServiceTest : public ::testing::Test {
 protected:
  void SetUp() override {
    gateway_ = std::make_unique<NiceMock<MockPaymentGateway>>();
    service_ = std::make_unique<OrderService>(gateway_.get());
  }

  std::unique_ptr<MockPaymentGateway> gateway_;
  std::unique_ptr<OrderService> service_;
};

// Test naming: <Method>_<Scenario>_<ExpectedBehavior>
TEST_F(OrderServiceTest, ProcessPayment_WithValidCard_ReturnsConfirmation) {
  // Arrange
  EXPECT_CALL(*gateway_, Charge(100.0, "tok_visa"))
    .WillOnce(Return(PaymentResult{.id = "pay_123", .status = PaymentStatus::kSucceeded}));

  // Act
  auto result = service_->ProcessPayment("order-1", "tok_visa");

  // Assert
  ASSERT_TRUE(result.has_value());
  EXPECT_EQ(result->payment_id, "pay_123");
}

TEST_F(OrderServiceTest, ProcessPayment_WhenGatewayFails_ReturnsNullopt) {
  EXPECT_CALL(*gateway_, Charge(_, _))
    .WillOnce(Return(PaymentResult{.status = PaymentStatus::kFailed}));

  auto result = service_->ProcessPayment("order-1", "tok_fail");

  EXPECT_FALSE(result.has_value());
}

// Parameterized tests
class OrderValidationTest : public ::testing::TestWithParam<std::string> {};

TEST_P(OrderValidationTest, ValidateOrder_WithInvalidId_ReturnsFalse) {
  Order order(GetParam(), 100.0);
  EXPECT_FALSE(order.IsValid());
}

INSTANTIATE_TEST_SUITE_P(
  InvalidIds, OrderValidationTest,
  ::testing::Values("", " ", "  ", "a", std::string(300, 'x'))
);
```

## CMakeLists.txt for Tests

```cmake
include(FetchContent)
FetchContent_Declare(googletest
  URL https://github.com/google/googletest/archive/refs/heads/main.zip)
FetchContent_MakeAvailable(googletest)

enable_testing()

add_executable(order_service_test
  test/order_service_test.cc
)

target_link_libraries(order_service_test
  order_service
  GTest::gtest_main
  GTest::gmock
)

include(GoogleTest)
gtest_discover_tests(order_service_test)
```
