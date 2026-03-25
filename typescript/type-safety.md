# TypeScript Type Safety

## Narrowing Patterns

```typescript
// Discriminated unions — exhaustive pattern matching
type Shape =
  | { kind: 'circle'; radius: number }
  | { kind: 'rectangle'; width: number; height: number }
  | { kind: 'triangle'; base: number; height: number };

function calculateArea(shape: Shape): number {
  switch (shape.kind) {
    case 'circle': return Math.PI * shape.radius ** 2;
    case 'rectangle': return shape.width * shape.height;
    case 'triangle': return 0.5 * shape.base * shape.height;
    default: {
      // TypeScript exhaustiveness check — compile error if new Shape added
      const _exhaustive: never = shape;
      throw new Error(`Unknown shape: ${JSON.stringify(_exhaustive)}`);
    }
  }
}
```

## Zod for Runtime Validation + Type Inference

```typescript
import { z } from 'zod';

// Define schema once — generates both runtime validator and TypeScript type
const CreateOrderSchema = z.object({
  userId: z.string().uuid(),
  items: z.array(z.object({
    productId: z.string().uuid(),
    quantity: z.number().int().positive().max(100),
    unitPrice: z.number().positive(),
  })).min(1).max(100),
  currency: z.enum(['USD', 'EUR', 'GBP']),
  discountCode: z.string().optional(),
});

type CreateOrderDto = z.infer<typeof CreateOrderSchema>;

// Usage at the HTTP boundary
function createOrderHandler(req: Request, res: Response) {
  const result = CreateOrderSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(422).json({ errors: result.error.flatten() });
  }
  // result.data is fully typed as CreateOrderDto
  return orderService.createOrder(result.data);
}
```

## Template Literal Types

```typescript
// Enforce naming conventions at the type level
type EventName = `${string}.${string}`; // e.g. 'order.created', 'payment.failed'
type CssVariable = `--${string}`;
type ApiRoute = `/api/v${number}/${string}`;

function publish(event: EventName, payload: unknown): void { ... }
publish('order.created', { id: '123' }); // ✅
publish('ordercreated', {});             // ❌ TypeScript error
```

## Conditional Types

```typescript
// Extract the resolved type from a Promise
type Awaited<T> = T extends Promise<infer U> ? U : T;

// Make specific keys required
type RequireFields<T, K extends keyof T> = T & Required<Pick<T, K>>;
type OrderWithId = RequireFields<Partial<Order>, 'id'>;
```
