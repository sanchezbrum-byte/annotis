# C++ AI Rules

> Full reference: `cpp/style-guide.md`

---

## Formatting (Google C++ Style)

- Line limit: **80 chars**
- Indentation: **2 spaces**
- Access specifiers indented 1 space: ` public:`, ` private:`
- File extensions: `.cc` source, `.h` header
- Use `#pragma once` for include guards

## Naming

| Concept | Style | Example |
|---------|-------|---------|
| Types (class/struct/enum) | `PascalCase` | `OrderService`, `PaymentResult` |
| Functions | `CamelCase()` | `ProcessOrder()`, `GetTotal()` |
| Variables | `snake_case` | `order_id`, `total_price` |
| Member variables | `snake_case_` (trailing `_`) | `order_id_`, `total_` |
| Constants | `kCamelCase` | `kMaxRetries`, `kDefaultTimeout` |
| Namespaces | `snake_case` | `myapp::orders` |

## Memory Management (C++ Core Guidelines)

```cpp
// ✅ GOOD: smart pointers — never raw new/delete
auto service = std::make_unique<OrderService>(repo.get());
auto config = std::make_shared<AppConfig>(configPath);

// ❌ NEVER in application code
Order* order = new Order(id, total);  // manual memory = leaks
delete order;

// ✅ RAII: resources owned by objects
std::ifstream file(path);  // closes automatically
```

## Error Handling

```cpp
// C++23 std::expected (no exceptions policy)
[[nodiscard]] std::expected<Order, std::error_code> FindOrder(const std::string& id);

// Use [[nodiscard]] on functions returning error codes
[[nodiscard]] absl::Status ValidateOrder(const Order& order);
```

## Unsafe Code

```cpp
// Every unsafe block requires a SAFETY comment
// SAFETY: We have exclusive access via Box::into_raw() and pointer has not been aliased.
auto value = unsafe_operation(ptr);
```

## Security

```cpp
// ❌ FORBIDDEN: buffer-overflow risk
scanf("%s", buffer);
gets(buffer);

// ✅ SAFE: bounds-checked
std::string input;
std::cin >> input;

// ✅ Array bounds: use .at() in debug builds
vec.at(index);  // throws out_of_range if invalid
```

## Tooling

```bash
clang-format -i **/*.cc **/*.h  # format
clang-tidy **/*.cc               # lint
cmake --build . --target test    # test
```
