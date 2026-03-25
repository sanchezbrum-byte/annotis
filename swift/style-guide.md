# Swift Style Guide

> **Sources:** Apple Swift API Design Guidelines (swift.org/documentation/api-design-guidelines), Google Swift Style Guide (google.github.io/swift), Airbnb Swift Style Guide (github.com/airbnb/swift)

---

## A. Formatting & Style

### Line Length

**100 characters** hard limit (Google Swift Style Guide). SwiftLint enforces this.

### Indentation

**2 spaces** (Google Swift Style Guide). Never tabs.

### Trailing Closures

```swift
// ✅ GOOD: trailing closure syntax when last argument is a closure
let sortedOrders = orders.sorted { $0.createdAt < $1.createdAt }

// ✅ GOOD: label the closure when there are multiple
UIView.animate(withDuration: 0.3) {
    self.view.alpha = 0
} completion: { _ in
    self.view.removeFromSuperview()
}
```

### Semicolons

**Never use semicolons.** Swift doesn't require them.

---

## B. Naming Conventions (Apple Swift API Design Guidelines)

| Concept | Convention | Example |
|---------|-----------|---------|
| Types (class, struct, enum, protocol) | `UpperCamelCase` | `OrderService`, `PaymentResult` |
| Functions, methods, properties | `lowerCamelCase` | `processPayment`, `isActive` |
| Constants | `lowerCamelCase` | `maxRetries`, `defaultCurrency` |
| Global constants | `lowerCamelCase` or `UPPER_SNAKE_CASE` for C-style | Same as local constants |
| Enum cases | `lowerCamelCase` (Swift 3+) | `.pending`, `.paid`, `.failed` |
| Protocols (capability) | Adjective or noun + `able/ible/ing` | `Codable`, `Hashable`, `Identifiable` |
| Protocols (role) | Noun | `OrderRepository`, `PaymentGateway` |

### Clarity at the Call Site (Apple API Design Guidelines)

```swift
// ✅ GOOD: fluent English phrase at call site
ordersArray.insert(order, at: 0)           // "insert order at zero"
let users = users.filter { $0.isActive }   // "users where isActive"

// ❌ BAD: omitting necessary words
x.insert(y, 0)        // what does 0 mean?
x.removeBoxes(3)      // removes 3 boxes, or box at index 3?
```

### Boolean Naming

```swift
// ✅ GOOD: reads as assertion
var isLoading: Bool
var hasActiveSubscription: Bool
var canSubmitOrder: Bool

// ❌ BAD
var loading: Bool
var subscription: Bool
```

---

## C. Types & Safety

### Prefer `struct` Over `class` for Value Types

```swift
// ✅ GOOD: immutable value object as struct
struct Money: Equatable, Hashable {
    let amount: Decimal
    let currency: Currency

    init(amount: Decimal, currency: Currency) throws {
        guard amount >= 0 else { throw MoneyError.negativeAmount }
        self.amount = amount
        self.currency = currency
    }

    func adding(_ other: Money) throws -> Money {
        guard self.currency == other.currency else {
            throw MoneyError.currencyMismatch
        }
        return try Money(amount: self.amount + other.amount, currency: self.currency)
    }
}
```

### Never Force Unwrap in Production

```swift
// ❌ BAD: crashes at runtime if nil
let user = users.first!
let price = order.total!
let url = URL(string: urlString)!

// ✅ GOOD: guard and handle the nil case
guard let user = users.first else {
    throw OrderError.noUsersFound
}

guard let url = URL(string: urlString) else {
    throw ValidationError.invalidURL(urlString)
}
```

### Use `guard` for Early Exit

```swift
// ✅ GOOD: guard reduces nesting
func processPayment(_ request: PaymentRequest) async throws -> PaymentConfirmation {
    guard !request.orderId.isEmpty else {
        throw PaymentError.invalidRequest("orderId is required")
    }
    guard let order = await orderRepo.findById(request.orderId) else {
        throw PaymentError.orderNotFound(request.orderId)
    }
    guard order.status == .pending else {
        throw PaymentError.orderNotPayable(order.status)
    }

    return try await paymentGateway.charge(order.total, cardToken: request.cardToken)
}
```

### Enums for State Machines

```swift
// ✅ GOOD: enum with associated values
enum OrderStatus: Equatable {
    case pending
    case paid(paymentId: String, paidAt: Date)
    case cancelled(reason: String, cancelledAt: Date)
    case refunded(refundId: String, amount: Decimal)
}

// ✅ GOOD: exhaustive switch — compiler errors if new case added
func displayStatus(_ status: OrderStatus) -> String {
    switch status {
    case .pending: return "Awaiting payment"
    case .paid(_, let date): return "Paid on \(date.formatted())"
    case .cancelled(let reason, _): return "Cancelled: \(reason)"
    case .refunded(_, let amount): return "Refunded \(amount)"
    }
}
```

---

## D. Comments & Documentation

### Swift DocC Format

```swift
/// Process a payment for an existing pending order.
///
/// Validates the order status, charges the payment gateway, and publishes
/// a `PaymentProcessedEvent`. Uses `async/await` for the gateway call.
///
/// - Parameters:
///   - orderId: The ID of the order to process. Must not be empty.
///   - cardToken: Tokenized card from the payment provider.
/// - Returns: A `PaymentConfirmation` with the payment ID and status.
/// - Throws:
///   - `PaymentError.orderNotFound` if no order with `orderId` exists.
///   - `PaymentError.orderNotPayable` if the order is not in `.pending` status.
///   - `PaymentError.declined` if the payment gateway declines the charge.
func processPayment(orderId: String, cardToken: String) async throws -> PaymentConfirmation
```

---

## E. Error Handling

```swift
// ✅ GOOD: typed errors with associated values
enum PaymentError: LocalizedError {
    case orderNotFound(String)
    case orderNotPayable(OrderStatus)
    case declined(code: String)
    case serviceUnavailable(underlying: Error)

    var errorDescription: String? {
        switch self {
        case .orderNotFound(let id): return "Order \(id) not found"
        case .orderNotPayable(let status): return "Order cannot be paid (status: \(status))"
        case .declined(let code): return "Payment declined: \(code)"
        case .serviceUnavailable: return "Payment service is temporarily unavailable"
        }
    }
}
```

---

## F. Swift Concurrency (async/await)

```swift
// ✅ GOOD: structured concurrency with async let for parallel execution
func loadDashboard(userId: String) async throws -> Dashboard {
    async let user = userService.fetchUser(userId)
    async let orders = orderService.fetchOrders(userId)
    async let notifications = notificationService.fetchUnread(userId)

    return Dashboard(
        user: try await user,
        orders: try await orders,
        notifications: try await notifications
    )
}

// ✅ GOOD: Task groups for dynamic parallelism
func fetchAllOrders(userIds: [String]) async throws -> [Order] {
    try await withThrowingTaskGroup(of: [Order].self) { group in
        for userId in userIds {
            group.addTask { try await orderService.fetchOrders(userId) }
        }
        return try await group.reduce(into: []) { $0 += $1 }
    }
}
```

---

## G. Security

```swift
// ❌ BAD: storing secret in code
let apiKey = "sk_live_abc123"

// ✅ GOOD: from Keychain or Info.plist (loaded from CI secrets)
let apiKey = KeychainManager.shared.getValue(for: .apiKey)

// ✅ GOOD: secure network requests (ATS enforced by default in iOS)
// Ensure NSAppTransportSecurity allows only HTTPS in Info.plist

// ✅ GOOD: sensitive data in Keychain, not UserDefaults
KeychainManager.shared.save(token, for: .authToken)
// Not: UserDefaults.standard.set(token, forKey: "auth_token") // ❌ not encrypted
```
