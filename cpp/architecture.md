# C++ Architecture

## Project Structure

```
project/
  src/
    domain/
      order.h / order.cc
      order_repository.h         # Abstract interface
      payment_gateway.h          # Abstract interface
    application/
      submit_order.h / .cc       # Use case
    adapters/
      persistence/
        postgres_order_repo.h / .cc
      http/
        order_controller.h / .cc
    shared/
      error.h                    # Error types
      result.h                   # Result<T, E> template
  test/
    domain/
      order_test.cc
    application/
      submit_order_test.cc
  CMakeLists.txt
```

## Interface Pattern (Pure Virtual)

```cpp
// domain/order_repository.h
#pragma once
#include <optional>
#include <string>
#include "order.h"

namespace myapp {

class OrderRepository {
 public:
  virtual ~OrderRepository() = default;

  virtual std::optional<Order> FindById(const std::string& id) const = 0;
  virtual void Save(const Order& order) = 0;
};

}  // namespace myapp
```

## Dependency Injection

```cpp
// application/submit_order.cc
class SubmitOrderUseCase {
 public:
  // Constructor injection — non-owning pointers (repository owned by caller)
  SubmitOrderUseCase(OrderRepository* order_repo, PaymentGateway* payment_gateway)
    : order_repo_(order_repo), payment_gateway_(payment_gateway) {}

 private:
  OrderRepository* order_repo_;       // non-owning
  PaymentGateway* payment_gateway_;   // non-owning
};
```
