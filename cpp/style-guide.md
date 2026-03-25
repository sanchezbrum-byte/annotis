# C++ Style Guide

> **Sources:** Google C++ Style Guide (google.github.io/styleguide/cppguide.html), C++ Core Guidelines (Bjarne Stroustrup + Herb Sutter, isocpp.github.io/CppCoreGuidelines), LLVM Coding Standards

---

## A. Formatting & Style

### Line Length

**80 characters** hard limit (Google C++ Style Guide §Formatting).

> LLVM recommends 80 characters. C++ Core Guidelines don't specify but recommend keeping lines short. We adopt Google's 80 as the hard limit.

### Indentation

- **2 spaces** per level (Google C++ Style Guide)
- Never use tabs
- Continuation lines: align with open parenthesis, or use 4-space hanging indent

### Header Files

Use `#pragma once` for include guards:

```cpp
// ✅ GOOD: modern include guard
#pragma once

#include <string>
#include <memory>

namespace myapp {

class OrderService {
 public:
  // ...
};

}  // namespace myapp
```

**Rules (Google C++ Style Guide §Header Files):**
- Every `.cc` file should have a corresponding `.h` header
- Header files should be self-contained (include all their own dependencies)
- Use forward declarations to reduce compile-time dependencies
- Never put `using namespace` in a header file

### Brace Style

```cpp
// ✅ GOOD: Google C++ style — brace on same line
class Order {
 public:
  Order(std::string id, double total) : id_(std::move(id)), total_(total) {}

  bool IsValid() const {
    return !id_.empty() && total_ > 0.0;
  }

 private:
  std::string id_;
  double total_;
};

// Function body brace on same line:
void ProcessOrder(const Order& order) {
  if (!order.IsValid()) {
    return;
  }
  // ...
}
```

### Spaces

- Space after keywords: `if (`, `for (`, `while (` — but NOT after function names: `func(arg)`
- Space around binary operators: `a + b`, `x = y`, `i < n`
- No space before `:` in class access specifiers, but indent class members by 1 space:

```cpp
class Foo {
 public:   // 1 space indent for access specifiers
  void Bar();
 private:
  int value_;
};
```

---

## B. Naming Conventions (Google C++ Style Guide §Naming)

| Concept | Convention | Example |
|---------|-----------|---------|
| Files | `snake_case.cc` / `snake_case.h` | `order_service.cc`, `payment_gateway.h` |
| Types (class, struct, enum) | `PascalCase` | `OrderService`, `PaymentResult` |
| Variables | `snake_case` | `order_id`, `total_price` |
| Class member variables | `snake_case_` (trailing `_`) | `order_id_`, `total_price_` |
| Constants | `kCamelCase` | `kMaxRetries`, `kDefaultTimeout` |
| Functions | `CamelCase()` | `ProcessOrder()`, `GetTotal()` |
| Namespaces | `snake_case` | `myapp::orders`, `myapp::payment` |
| Enumerators | `kCamelCase` | `kPending`, `kPaid`, `kFailed` |
| Macros | `UPPER_SNAKE_CASE` | `MAX_ORDER_SIZE`, `DISALLOW_COPY` |

### Boolean Naming

```cpp
bool is_active_;
bool has_subscription_;
bool should_retry_;

// Method names: IsXxx(), HasXxx(), CanXxx()
bool IsValid() const;
bool HasActiveSubscription() const;
```

---

## C. Functions

### Single Responsibility & Length

Maximum ~50 lines per function. Split larger functions into named helpers.

### Pass-by-Value vs Reference vs Pointer (C++ Core Guidelines F.15–F.22)

| Input Type | Recommendation |
|-----------|---------------|
| Cheap to copy (int, double, pointer) | Pass by value |
| Expensive to copy, read only | Pass by const reference (`const Foo&`) |
| May be null / ownership unclear | Pass by pointer (`Foo*`) |
| Caller transfers ownership | Pass by value (std::move at call site) or `unique_ptr<Foo>` |
| Output parameter | Prefer returning by value; use `out*` param only for performance |

```cpp
// ✅ GOOD: const reference for read-only expensive object
void LogOrder(const Order& order);

// ✅ GOOD: pass unique_ptr to transfer ownership
void ProcessOrder(std::unique_ptr<Order> order);

// ❌ BAD: non-const reference as output parameter (unclear at call site)
void GetUserName(std::string& name); // unclear if name is in or out

// ✅ GOOD: return by value
std::string GetUserName(const UserId& id);
```

### Return Error Information

Without exceptions: use `std::expected` (C++23), `absl::StatusOr`, or a custom Result type:

```cpp
// ✅ C++23 std::expected
#include <expected>

std::expected<Order, std::error_code> FindOrder(const std::string& id) {
  auto* order = repository_.Find(id);
  if (!order) {
    return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
  }
  return *order;
}

// Caller:
auto result = FindOrder(orderId);
if (!result) {
  LOG(ERROR) << "Order not found: " << result.error().message();
  return;
}
ProcessOrder(result.value());
```

---

## D. Comments & Documentation

### Doxygen-style Comments for Public APIs

```cpp
/// @brief Process a payment for an existing order.
///
/// Validates the order is in PENDING status, charges the payment gateway,
/// and transitions the order to PAID. Thread-safe.
///
/// @param order_id  The ID of the order to process. Must not be empty.
/// @param card_token Tokenized card from the payment provider.
/// @return ProcessPaymentResult with payment ID and status on success.
/// @return std::nullopt if the order is not found.
/// @throws PaymentDeclinedException if the payment gateway declines the charge.
std::optional<ProcessPaymentResult> ProcessPayment(
    const std::string& order_id, const std::string& card_token);
```

---

## E. Error Handling

Google C++ Style Guide prohibits exceptions for new code in many Google projects. Document your project's exception policy:

**Option A: No exceptions (Google style)**
- Use `absl::Status` / `absl::StatusOr<T>` or `std::expected<T, E>` (C++23)
- Check return values — use `[[nodiscard]]` on functions that return errors

```cpp
[[nodiscard]] absl::Status ValidateOrder(const Order& order);

// Caller must check the return value or compilation warning
auto status = ValidateOrder(order);
if (!status.ok()) {
  LOG(ERROR) << "Invalid order: " << status.message();
  return status;
}
```

**Option B: Exceptions enabled**
- Use RAII to ensure cleanup (no leak on throw)
- Only throw for exceptional conditions, not normal control flow
- Catch exceptions at component boundaries, not inside every function

---

## F. Modern C++ Patterns (C++17/20/23)

### Use `auto` for Readability, Not to Avoid Types

```cpp
// ✅ GOOD: auto avoids verbose iterator type
for (auto& order : orders) { ... }
auto it = order_map.find(id);

// ❌ BAD: auto hides important type information
auto result = ProcessPayment(orderId, token); // what does result contain?

// ✅ GOOD: explicit for return values
PaymentResult result = ProcessPayment(orderId, token);
```

### Structured Bindings (C++17)

```cpp
// ✅ GOOD: structured bindings for map iteration
for (const auto& [id, order] : order_map) {
  LOG(INFO) << "Order " << id << " total: " << order.Total();
}
```

### Range-Based Algorithms

```cpp
// ✅ GOOD: use std::ranges algorithms
std::ranges::sort(orders, {}, &Order::CreatedAt);
auto pending = orders | std::views::filter(&Order::IsPending);
```

---

## G. Security

- **Never use `scanf`, `gets`, `sprintf`** — buffer overflow risks; use `std::cin`, `std::string`, `std::format` (C++20)
- **Validate all array/vector indexing** — use `.at()` in debug builds instead of `[]` to get bounds checking
- **Don't trust integer arithmetic** — check for overflow with `__builtin_add_overflow` or safe integer libraries
- **Avoid `system()`** — command injection risk; use POSIX `exec*` family or platform APIs

---

## H. Performance

- Prefer move semantics over copy for expensive objects
- Avoid virtual dispatch in hot paths — use template-based polymorphism (CRTP) for zero-cost abstractions
- Profile before optimizing — use `perf`, `gprof`, or Google's `gperftools`
- Big-O comment for any non-trivial algorithm
