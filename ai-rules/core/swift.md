# Swift AI Rules

> Full reference: `swift/style-guide.md`

---

## Formatting (SwiftLint)

- Line limit: **100 chars** (Google Swift Style)
- Indentation: **2 spaces**
- Semicolons: **never**
- Use trailing closures; always use braces

## Naming (Apple API Design Guidelines)

| Concept | Style | Example |
|---------|-------|---------|
| Types/protocols | `UpperCamelCase` | `OrderService`, `Identifiable` |
| Functions/properties | `lowerCamelCase` | `processPayment`, `isActive` |
| Enum cases | `lowerCamelCase` | `.pending`, `.paid`, `.failed` |
| Booleans | `is/has/can/should` | `isLoading`, `hasSubscription` |

## Safety

```swift
// ❌ NEVER force unwrap in production
let price = order.total!      // crashes if nil

// ✅ guard let for early exit
guard let order = orders.first else {
    throw OrderError.notFound
}

// ✅ if let for optional binding
if let discount = order.discount {
    applyDiscount(discount)
}
```

## Enums for Exhaustive State

```swift
// ✅ Discriminated union with associated values
enum OrderStatus {
    case pending
    case paid(paymentId: String, paidAt: Date)
    case cancelled(reason: String)
}

// ✅ Exhaustive switch — compiler catches missing cases
switch status {
case .pending: ...
case .paid(_, let date): ...
case .cancelled(let reason): ...
}
```

## Concurrency (Swift 5.5+)

```swift
// ✅ async/await for all async operations
func loadDashboard(userId: String) async throws -> Dashboard {
    async let user = userService.fetchUser(userId)
    async let orders = orderService.fetchOrders(userId)
    return Dashboard(user: try await user, orders: try await orders)
}

// ✅ @MainActor for UI updates
@MainActor
func updateUI(with orders: [Order]) { ... }
```

## Security

```swift
// Keychain for sensitive data (NOT UserDefaults)
KeychainManager.shared.save(token, for: .authToken)

// HTTPS enforced by App Transport Security (ATS) — never disable NSAllowsArbitraryLoads in production
```

## Tooling

```bash
swiftlint         # lint
swift build       # build
swift test        # test
```
