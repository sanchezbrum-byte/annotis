# TypeScript Testing Standards

> **Tools:** Jest + ts-jest OR Vitest (preferred for new projects), Zod for schema validation in tests

---

## Vitest (Recommended for new TypeScript projects)

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      thresholds: { lines: 80, branches: 80, functions: 80 },
      exclude: ['**/migrations/**', '**/index.ts'],
    },
  },
});
```

## Type-Safe Test Factories

```typescript
// tests/factories/orderFactory.ts
import type { Order } from '../../src/features/orders/domain/order.js';
import { OrderStatus } from '../../src/features/orders/domain/order.js';

export function buildOrder(overrides: Partial<Order> = {}): Order {
  return {
    id: 'order-123' as OrderId,
    userId: 'user-456' as UserId,
    items: [buildOrderItem()],
    total: { amount: 100, currency: 'USD' },
    status: OrderStatus.Pending,
    createdAt: new Date('2025-01-01T00:00:00Z'),
    ...overrides,
  };
}
```

## Mock Repository (Fake, not Mock)

```typescript
// tests/fakes/fakeOrderRepository.ts
import type { OrderRepository } from '../../src/features/orders/domain/orderRepository.js';
import type { Order } from '../../src/features/orders/domain/order.js';

export class FakeOrderRepository implements OrderRepository {
  private readonly store = new Map<string, Order>();

  async findById(id: string): Promise<Order | null> {
    return this.store.get(id) ?? null;
  }

  async save(order: Order): Promise<Order> {
    this.store.set(order.id, order);
    return order;
  }

  // Test helper: seed data
  seed(order: Order): void {
    this.store.set(order.id, order);
  }
}
```

## Full Test File

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { CreateOrderUseCase } from '../../src/features/orders/application/createOrder.js';
import { FakeOrderRepository } from '../fakes/fakeOrderRepository.js';
import { buildOrder, buildCreateOrderParams } from '../factories/orderFactory.js';
import { ValidationError } from '../../src/shared/domain/DomainError.js';

describe('CreateOrderUseCase', () => {
  let orderRepo: FakeOrderRepository;
  let eventBus: { publish: ReturnType<typeof vi.fn> };
  let useCase: CreateOrderUseCase;

  beforeEach(() => {
    orderRepo = new FakeOrderRepository();
    eventBus = { publish: vi.fn().mockResolvedValue(undefined) };
    useCase = new CreateOrderUseCase(orderRepo, eventBus);
  });

  it('returns created order with pending status for valid params', async () => {
    const params = buildCreateOrderParams();
    const result = await useCase.execute(params);
    expect(result.status).toBe('pending');
    expect(result.userId).toBe(params.userId);
  });

  it('persists the order to the repository', async () => {
    const params = buildCreateOrderParams();
    const result = await useCase.execute(params);
    const saved = await orderRepo.findById(result.id);
    expect(saved).not.toBeNull();
  });

  it('throws ValidationError for empty items', async () => {
    await expect(
      useCase.execute(buildCreateOrderParams({ items: [] })),
    ).rejects.toThrow(ValidationError);
  });
});
```
