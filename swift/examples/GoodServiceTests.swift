import XCTest
@testable import OrdersModule

// ✅ Test doubles as nested structs — lightweight, explicit, no third-party mock library needed
final class OrderPaymentServiceTests: XCTestCase {

    // -------------------------------------------------------------------------
    // Test doubles
    // -------------------------------------------------------------------------

    final class FakeOrderRepository: OrderRepositoryProtocol {
        var orders: [String: Order] = [:]
        var savedOrders: [Order] = []

        func findOrder(byID id: String) async throws -> Order? {
            orders[id]
        }

        func save(_ order: Order) async throws {
            savedOrders.append(order)
            orders[order.id] = order
        }
    }

    final class StubPaymentGateway: PaymentGatewayProtocol {
        var result: Result<String, Error> = .success("pay-789")

        func charge(amount: Decimal, currency: String, cardToken: String) async throws -> String {
            try result.get()
        }
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    func makePendingOrder(id: String = "order-123") throws -> Order {
        Order(
            id: id,
            userID: "user-456",
            total: try Money(amount: 100, currency: "USD"),
            status: .pending
        )
    }

    func makeService(
        repository: FakeOrderRepository,
        gateway: StubPaymentGateway
    ) -> OrderPaymentService {
        OrderPaymentService(orderRepository: repository, paymentGateway: gateway)
    }

    // -------------------------------------------------------------------------
    // Happy path
    // -------------------------------------------------------------------------

    func test_processPayment_validCard_returnsPaymentID() async throws {
        // Arrange
        let repo = FakeOrderRepository()
        let order = try makePendingOrder()
        repo.orders[order.id] = order
        let gateway = StubPaymentGateway()
        let service = makeService(repository: repo, gateway: gateway)

        // Act
        let paymentID = try await service.processPayment(orderID: order.id, cardToken: "tok_visa")

        // Assert
        XCTAssertEqual(paymentID, "pay-789")
        XCTAssertEqual(repo.savedOrders.last?.status, .paid)
    }

    // -------------------------------------------------------------------------
    // Error cases
    // -------------------------------------------------------------------------

    func test_processPayment_orderNotFound_throwsOrderNotFound() async throws {
        let repo = FakeOrderRepository() // empty — no orders
        let service = makeService(repository: repo, gateway: StubPaymentGateway())

        do {
            _ = try await service.processPayment(orderID: "missing", cardToken: "tok_visa")
            XCTFail("Expected PaymentError.orderNotFound to be thrown")
        } catch PaymentError.orderNotFound(let id) {
            XCTAssertEqual(id, "missing")
        }
    }

    func test_processPayment_alreadyPaid_throwsOrderNotPayable() async throws {
        let repo = FakeOrderRepository()
        var order = try makePendingOrder()
        order.markAsPaid(paymentID: "pay-old")
        repo.orders[order.id] = order
        let service = makeService(repository: repo, gateway: StubPaymentGateway())

        do {
            _ = try await service.processPayment(orderID: order.id, cardToken: "tok_visa")
            XCTFail("Expected PaymentError.orderNotPayable to be thrown")
        } catch PaymentError.orderNotPayable(let id, let status) {
            XCTAssertEqual(id, order.id)
            XCTAssertEqual(status, .paid)
        }
    }

    func test_processPayment_gatewayDeclines_throwsCardDeclined() async throws {
        let repo = FakeOrderRepository()
        repo.orders["order-123"] = try makePendingOrder()

        let gateway = StubPaymentGateway()
        gateway.result = .failure(PaymentError.cardDeclined("insufficient_funds"))

        let service = makeService(repository: repo, gateway: gateway)

        do {
            _ = try await service.processPayment(orderID: "order-123", cardToken: "tok_declined")
            XCTFail("Expected PaymentError.cardDeclined to be thrown")
        } catch PaymentError.cardDeclined(let code) {
            XCTAssertEqual(code, "insufficient_funds")
        }

        // ✅ Data integrity: no save when payment fails
        XCTAssertTrue(repo.savedOrders.isEmpty)
    }

    func test_processPayment_gatewayUnavailable_throwsServiceUnavailable() async throws {
        let repo = FakeOrderRepository()
        repo.orders["order-123"] = try makePendingOrder()

        let gateway = StubPaymentGateway()
        gateway.result = .failure(URLError(.timedOut))

        let service = makeService(repository: repo, gateway: gateway)

        do {
            _ = try await service.processPayment(orderID: "order-123", cardToken: "tok_visa")
            XCTFail("Expected PaymentError.serviceUnavailable to be thrown")
        } catch PaymentError.serviceUnavailable {
            // expected
        }
    }
}
