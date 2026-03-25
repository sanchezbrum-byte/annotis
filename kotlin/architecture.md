# Kotlin Architecture

## Android Clean Architecture (MVVM)

```
app/
  features/
    orders/
      domain/
        Order.kt
        OrderRepository.kt      # Interface
        GetOrdersUseCase.kt
      data/
        OrderRepositoryImpl.kt  # Implements interface
        remote/
          OrderApiService.kt    # Retrofit
          OrderDto.kt
        local/
          OrderEntity.kt        # Room entity
          OrderDao.kt
      presentation/
        OrderListFragment.kt
        OrderListViewModel.kt
        OrderListState.kt
  shared/
    domain/
      Result.kt
      BaseUseCase.kt
    data/
      NetworkClient.kt
    di/
      AppModule.kt              # Hilt modules
```

## Dependency Injection (Hilt)

```kotlin
@HiltViewModel
class OrderListViewModel @Inject constructor(
    private val getOrdersUseCase: GetOrdersUseCase,
) : ViewModel() { ... }

@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {
    @Provides
    @Singleton
    fun provideOrderRepository(
        apiService: OrderApiService,
        dao: OrderDao,
    ): OrderRepository = OrderRepositoryImpl(apiService, dao)
}
```
