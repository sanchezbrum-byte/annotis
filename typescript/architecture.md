# TypeScript Architecture

## Project Structure (Node.js / API)

See also `universal/architecture.md` for Clean Architecture principles.

```
src/
  features/
    orders/
      index.ts                    # Public barrel export
      domain/
        order.ts                  # Order entity + domain types
        orderRepository.ts        # Repository interface (Port)
        errors.ts                 # Domain error classes
      application/
        createOrder.ts            # Use case
        processPayment.ts         # Use case
        dtos.ts                   # Input/output DTOs
      adapters/
        http/
          ordersRouter.ts         # Express/Fastify router
          ordersController.ts     # HTTP handlers
          ordersSchemas.ts        # Zod schemas for HTTP boundary
        persistence/
          postgresOrderRepo.ts    # Repository implementation
          orderMapper.ts          # Domain ↔ DB model mapping
  shared/
    domain/
      BaseEntity.ts
      ValueObject.ts
      DomainError.ts
    infrastructure/
      database/
        connection.ts
        migrations/
      logger.ts
      config.ts
  app.ts                          # App factory
  server.ts                       # Entry point
```

## Dependency Injection with tsyringe or manual

```typescript
// Manual DI (preferred for simplicity)
// app.ts
import { PostgresOrderRepository } from './features/orders/adapters/persistence/postgresOrderRepo.js';
import { CreateOrderUseCase } from './features/orders/application/createOrder.js';
import { createOrdersRouter } from './features/orders/adapters/http/ordersRouter.js';

export function createApp(): Express {
  const app = express();

  // Wire dependencies
  const orderRepo = new PostgresOrderRepository(db);
  const createOrder = new CreateOrderUseCase(orderRepo, eventBus);
  const ordersRouter = createOrdersRouter({ createOrder });

  app.use('/orders', ordersRouter);
  return app;
}
```

## Feature Module Pattern

```typescript
// features/orders/domain/order.ts
export interface Order {
  readonly id: OrderId;
  readonly userId: UserId;
  readonly items: readonly OrderItem[];
  readonly total: Money;
  readonly status: OrderStatus;
  readonly createdAt: Date;
}

export function createOrder(
  params: CreateOrderParams,
): Order {
  // Domain validation
  if (params.items.length === 0) {
    throw new EmptyOrderError();
  }
  return {
    id: generateOrderId(),
    userId: params.userId,
    items: params.items,
    total: calculateTotal(params.items),
    status: OrderStatus.Pending,
    createdAt: new Date(),
  };
}
```
