# C++ Memory Management

> **Source:** C++ Core Guidelines R.* rules, "Effective Modern C++" (Scott Meyers)

---

## RAII — Resource Acquisition Is Initialization

Every resource (memory, file handles, locks, sockets) must be owned by an object whose destructor releases it. Never manage resources manually.

```cpp
// ❌ BAD: manual resource management — leaks on exception or early return
void ProcessFile(const std::string& path) {
  FILE* fp = fopen(path.c_str(), "r");
  // ... if an exception is thrown here, fp is never closed
  ProcessData(fp);
  fclose(fp); // never reached on exception
}

// ✅ GOOD: RAII — destructor guarantees cleanup
void ProcessFile(const std::string& path) {
  std::ifstream file(path); // RAII: closes on scope exit
  if (!file.is_open()) throw std::runtime_error("Cannot open file: " + path);
  ProcessData(file); // even if this throws, file closes
}
```

---

## Smart Pointers (C++ Core Guidelines R.20–R.30)

**Rule:** Never use raw `new` or `delete` in application code.

| Smart Pointer | Use Case | Ownership |
|--------------|---------|----------|
| `std::unique_ptr<T>` | Single owner | Exclusive ownership, moves |
| `std::shared_ptr<T>` | Multiple owners | Shared ownership with ref-count |
| `std::weak_ptr<T>` | Observer without ownership | Breaks cycles in shared_ptr graphs |
| `T&` or `T*` | Non-owning reference/view | Caller guarantees lifetime |

```cpp
// ✅ Factory: return unique_ptr from factory functions
std::unique_ptr<PaymentGateway> CreateStripeGateway(const std::string& apiKey) {
  return std::make_unique<StripeGateway>(apiKey);
}

// ✅ Injecting dependencies: pass as raw pointer or reference (non-owning)
class OrderService {
 public:
  // PaymentGateway* is a non-owning view — OrderService doesn't own it
  explicit OrderService(PaymentGateway* gateway) : gateway_(gateway) {}

 private:
  PaymentGateway* gateway_;  // non-owning; object lifetime managed elsewhere
};

// ✅ Shared ownership (rare — think twice before using shared_ptr)
auto config = std::make_shared<AppConfig>();
auto service_a = std::make_shared<ServiceA>(config);
auto service_b = std::make_shared<ServiceB>(config);
```

---

## Move Semantics

```cpp
// ✅ Move expensive objects to avoid copies
std::string BuildJson(std::vector<Order> orders) {
  // ... build JSON string
  return result; // NRVO or move — no copy
}

// ✅ std::move when transferring ownership
class OrderProcessor {
 public:
  explicit OrderProcessor(std::vector<Order> orders)
    : orders_(std::move(orders)) {}  // moves, not copies
 private:
  std::vector<Order> orders_;
};
```

---

## Common Memory Anti-Patterns

```cpp
// ❌ NEVER: raw new/delete in application code
Order* order = new Order(id, total);
// ... forgetting delete leaks; exceptions leak; complex lifetimes
delete order;

// ❌ NEVER: returning raw pointer to local variable
Order* GetOrder() {
  Order local_order("id", 100.0);
  return &local_order; // dangling pointer — UB
}

// ❌ NEVER: storing raw pointer longer than the pointee lives
std::vector<Order*> order_ptrs;
{
  Order temp("id", 100.0);
  order_ptrs.push_back(&temp); // temp destroyed at end of scope
}
// order_ptrs[0] is now a dangling pointer — UB
```
