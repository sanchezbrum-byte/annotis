import Foundation

// ✅ Domain model: immutable value type with validation
struct Money: Equatable {
    let amount: Decimal
    let currency: String

    init(amount: Decimal, currency: String) throws {
        guard amount >= 0 else {
            throw ValidationError.negativeAmount(amount)
        }
        guard currency.count == 3 else {
            throw ValidationError.invalidCurrency(currency)
        }
        self.amount = amount
        self.currency = currency
    }
}

// ✅ Typed errors — never use NSError or generic Error directly
enum ValidationError: LocalizedError {
    case negativeAmount(Decimal)
    case invalidCurrency(String)

    var errorDescription: String? {
        switch self {
        case .negativeAmount(let amount):
            return "Amount must be non-negative, got: \(amount)"
        case .invalidCurrency(let code):
            return "Currency must be ISO 4217 (3 chars), got: \(code)"
        }
    }
}

enum PaymentError: LocalizedError {
    case orderNotFound(String)
    case orderNotPayable(String, OrderStatus)
    case cardDeclined(String)
    case serviceUnavailable(underlying: Error)

    var errorDescription: String? {
        switch self {
        case .orderNotFound(let id):           return "Order \(id) not found"
        case .orderNotPayable(let id, let s):  return "Order \(id) is not payable (status: \(s))"
        case .cardDeclined(let code):          return "Card declined: \(code)"
        case .serviceUnavailable(let e):       return "Payment service unavailable: \(e)"
        }
    }
}

enum OrderStatus: String {
    case pending, paid, cancelled
}

// ✅ Protocol for dependency injection — enables easy test doubles
protocol OrderRepositoryProtocol {
    func findOrder(byID id: String) async throws -> Order?
    func save(_ order: Order) async throws
}

protocol PaymentGatewayProtocol {
    func charge(amount: Decimal, currency: String, cardToken: String) async throws -> String
}

// ✅ Final class — prevents unintended subclassing
final class OrderPaymentService {
    private let orderRepository: OrderRepositoryProtocol
    private let paymentGateway: PaymentGatewayProtocol

    init(orderRepository: OrderRepositoryProtocol, paymentGateway: PaymentGatewayProtocol) {
        self.orderRepository = orderRepository
        self.paymentGateway = paymentGateway
    }

    /// Process a payment for an existing pending order.
    ///
    /// - Parameters:
    ///   - orderID: The order to charge. Must not be empty.
    ///   - cardToken: Tokenised card from the payment provider.
    /// - Returns: The payment confirmation ID.
    /// - Throws: `PaymentError` describing the failure reason.
    func processPayment(orderID: String, cardToken: String) async throws -> String {
        // ✅ Guard for preconditions — fail fast, keep the happy path flat
        guard !orderID.isEmpty else {
            throw ValidationError.negativeAmount(0) // replace with proper precond error
        }

        guard let order = try await orderRepository.findOrder(byID: orderID) else {
            throw PaymentError.orderNotFound(orderID)
        }

        guard order.status == .pending else {
            throw PaymentError.orderNotPayable(orderID, order.status)
        }

        let paymentID: String
        do {
            paymentID = try await paymentGateway.charge(
                amount: order.total.amount,
                currency: order.total.currency,
                cardToken: cardToken
            )
        } catch let error as PaymentError {
            throw error // re-throw domain errors as-is
        } catch {
            throw PaymentError.serviceUnavailable(underlying: error)
        }

        var updatedOrder = order
        updatedOrder.markAsPaid(paymentID: paymentID)
        try await orderRepository.save(updatedOrder)

        return paymentID
    }
}

// ✅ Value type for domain entity — structs preferred for models in Swift
struct Order {
    let id: String
    let userID: String
    var total: Money
    var status: OrderStatus
    private(set) var paymentID: String?

    mutating func markAsPaid(paymentID: String) {
        self.status = .paid
        self.paymentID = paymentID
    }
}
