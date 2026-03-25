# Swift Testing Standards

> **Tools:** Swift Testing (Swift 6), XCTest (legacy)

---

## Swift Testing (Swift 6+, Preferred)

```swift
import Testing

@Suite("OrderViewModel Tests")
struct OrderViewModelTests {

    @Test("loads orders successfully for valid user")
    func loadsOrdersForValidUser() async throws {
        // Arrange
        let mockRepo = MockOrderRepository()
        let viewModel = OrderListViewModel(repo: mockRepo)
        mockRepo.stubbedOrders = [.pending(id: "o1"), .paid(id: "o2")]

        // Act
        await viewModel.loadOrders(userId: "u1")

        // Assert
        #expect(viewModel.orders.count == 2)
        #expect(viewModel.isLoading == false)
        #expect(viewModel.error == nil)
    }

    @Test("shows error when repository throws")
    func showsErrorOnRepositoryFailure() async {
        let mockRepo = MockOrderRepository()
        mockRepo.shouldThrow = OrderError.serviceUnavailable(underlying: URLError(.notConnectedToInternet))
        let viewModel = OrderListViewModel(repo: mockRepo)

        await viewModel.loadOrders(userId: "u1")

        #expect(viewModel.error != nil)
        #expect(viewModel.orders.isEmpty)
    }
}
```

## XCTest (Legacy / Compatibility)

```swift
import XCTest
@testable import MyApp

final class MoneyTests: XCTestCase {

    func test_adding_sameCurrency_returnsCorrectSum() throws {
        // Arrange
        let price = try Money(amount: 50.00, currency: .usd)
        let tax = try Money(amount: 5.00, currency: .usd)

        // Act
        let total = try price.adding(tax)

        // Assert
        XCTAssertEqual(total.amount, 55.00)
        XCTAssertEqual(total.currency, .usd)
    }

    func test_adding_differentCurrencies_throwsCurrencyMismatch() throws {
        let usd = try Money(amount: 50.00, currency: .usd)
        let eur = try Money(amount: 50.00, currency: .eur)
        XCTAssertThrowsError(try usd.adding(eur)) { error in
            XCTAssertEqual(error as? MoneyError, .currencyMismatch)
        }
    }
}
```
