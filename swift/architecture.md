# Swift Architecture

## MVVM + Clean Architecture (iOS)

```
Features/
  Orders/
    Domain/
      Order.swift              # Model (struct)
      OrderRepository.swift    # Protocol
    Application/
      OrderViewModel.swift     # ViewModel
      FetchOrdersUseCase.swift
    Adapters/
      Network/
        OrderAPIClient.swift   # Implements OrderRepository
      Persistence/
        CoreDataOrderRepo.swift
      UI/
        OrderListView.swift    # SwiftUI View
        OrderDetailView.swift
Shared/
  Domain/
    BaseError.swift
  Infrastructure/
    NetworkClient.swift
    KeychainManager.swift
```

## ViewModel Pattern (SwiftUI + Combine / Observable)

```swift
// ✅ @Observable macro (iOS 17+) — replaces ObservableObject
@Observable
final class OrderListViewModel {
    private(set) var orders: [Order] = []
    private(set) var isLoading = false
    private(set) var error: OrderError?

    private let fetchOrders: FetchOrdersUseCase

    init(fetchOrders: FetchOrdersUseCase) {
        self.fetchOrders = fetchOrders
    }

    @MainActor
    func loadOrders(userId: String) async {
        isLoading = true
        defer { isLoading = false }
        do {
            orders = try await fetchOrders.execute(userId: userId)
        } catch let orderError as OrderError {
            error = orderError
        } catch {
            self.error = .serviceUnavailable(underlying: error)
        }
    }
}
```
