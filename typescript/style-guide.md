# TypeScript Style Guide

> **Sources:** TypeScript official handbook (typescriptlang.org/docs), Airbnb TypeScript ESLint config, Google TypeScript Style Guide, Matt Pocock's Total TypeScript best practices

---

## A. Formatting & Style

Inherits all JavaScript formatting rules. See [../javascript/style-guide.md](../javascript/style-guide.md).

Additional TypeScript-specific rules:

- **100 character hard limit** (Airbnb/Prettier)
- **2 spaces** indentation
- **Semicolons** required
- **Single quotes** for strings

---

## B. Type System Rules

### Strict Mode (Required)

Every project must have these in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

`"strict": true` enables: `strictNullChecks`, `strictFunctionTypes`, `strictPropertyInitialization`, `noImplicitAny`, `noImplicitThis`, `alwaysStrict`.

### No `any`

```typescript
// ❌ BAD: any disables all type checking
function processData(data: any): any {
  return data.value; // no type safety
}

// ✅ GOOD: use unknown and narrow it
function processData(data: unknown): string {
  if (typeof data !== 'object' || data === null) {
    throw new TypeError('Expected an object');
  }
  if (!('value' in data) || typeof (data as { value: unknown }).value !== 'string') {
    throw new TypeError('Expected data.value to be a string');
  }
  return (data as { value: string }).value;
}

// ✅ BETTER: use a validated schema (Zod)
import { z } from 'zod';
const DataSchema = z.object({ value: z.string() });
function processData(data: unknown): string {
  return DataSchema.parse(data).value;
}
```

### Prefer `interface` for Object Shapes, `type` for Unions/Intersections

```typescript
// ✅ Interface for object shapes (extendable, better error messages)
interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
}

// ✅ Type alias for unions, intersections, mapped types
type PaymentStatus = 'pending' | 'processing' | 'paid' | 'failed' | 'refunded';
type OrderWithUser = Order & { user: User };
type ReadOnly<T> = { readonly [K in keyof T]: T[K] };
```

### Avoid `enum` — Use `const` Objects

```typescript
// ❌ BAD: enum has surprising runtime behavior and poor tree-shaking
enum OrderStatus {
  Pending = 'pending',
  Paid = 'paid',
}

// ✅ GOOD: const object + typeof
const OrderStatus = {
  Pending: 'pending',
  Paid: 'paid',
  Failed: 'failed',
} as const;

type OrderStatus = typeof OrderStatus[keyof typeof OrderStatus];
// type OrderStatus = 'pending' | 'paid' | 'failed'
```

### Avoid `as` Assertions

```typescript
// ❌ BAD: type assertion bypasses type checking
const user = (await fetchUser(id)) as User;

// ✅ GOOD: type guard (runtime check + type narrowing)
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value &&
    typeof (value as User).id === 'string'
  );
}

// ✅ BEST: Zod validation (both validates and narrows type)
const UserSchema = z.object({ id: z.string(), name: z.string() });
const user = UserSchema.parse(await fetchUser(id));
```

### Avoid Non-null Assertions (`!`)

```typescript
// ❌ BAD: non-null assertion crashes at runtime if value is null
const user = users.find((u) => u.id === id)!; // throws if not found

// ✅ GOOD: handle the null case
const user = users.find((u) => u.id === id);
if (!user) throw new NotFoundError(`User ${id} not found`);
```

---

## C. Naming Conventions

Inherits JavaScript naming conventions, plus:

| Concept | Convention | Example |
|---------|-----------|---------|
| Interfaces | `PascalCase` (no `I` prefix) | `User`, `OrderRepository` |
| Type aliases | `PascalCase` | `PaymentStatus`, `UserId` |
| Generic type params | Single letter or descriptive | `T`, `TItem`, `TKey`, `TValue` |
| Type predicates | `is<Type>` | `isUser`, `isOrder` |

```typescript
// ✅ Branded types for type-safe IDs
type UserId = string & { readonly __brand: 'UserId' };
type OrderId = string & { readonly __brand: 'OrderId' };

function createUserId(id: string): UserId {
  return id as UserId;
}

// Now you can't accidentally pass an OrderId where a UserId is expected
function getUser(id: UserId): Promise<User> { ... }
getUser(orderId); // ❌ TypeScript error — wrong brand
```

---

## D. Functions & Methods

### Always Annotate Return Types for Public Functions

```typescript
// ❌ BAD: inferred return type — breaks when refactoring
function getUser(id: string) {
  return userRepo.findById(id);
}

// ✅ GOOD: explicit return type — compiler error if implementation diverges
async function getUser(id: string): Promise<User | null> {
  return userRepo.findById(id);
}
```

### Function Overloads for Multiple Signatures

```typescript
// ✅ Use overloads instead of union params with complex conditionals
function format(value: Date): string;
function format(value: number, decimals: number): string;
function format(value: Date | number, decimals?: number): string {
  if (value instanceof Date) {
    return value.toISOString();
  }
  return value.toFixed(decimals ?? 2);
}
```

---

## E. Error Handling

### Result Type Pattern (for expected errors)

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

// ✅ Explicit error path — no exceptions for expected failures
async function parseUserInput(raw: unknown): Promise<Result<User>> {
  const parsed = UserSchema.safeParse(raw);
  if (!parsed.success) {
    return { ok: false, error: new ValidationError(parsed.error.message) };
  }
  return { ok: true, value: parsed.data };
}

// Caller knows it might fail
const result = await parseUserInput(body);
if (!result.ok) {
  return res.status(422).json({ error: result.error.message });
}
const user = result.value; // TypeScript knows this is User
```

---

## F. Generic Patterns

```typescript
// ✅ Generic repository interface
interface Repository<TEntity, TId = string> {
  findById(id: TId): Promise<TEntity | null>;
  save(entity: TEntity): Promise<TEntity>;
  delete(id: TId): Promise<void>;
}

// ✅ Utility types — use built-ins before rolling your own
type CreateOrderDto = Omit<Order, 'id' | 'createdAt' | 'status'>;
type UpdateOrderDto = Partial<Pick<Order, 'items' | 'currency'>>;
type ReadonlyOrder = Readonly<Order>;
```

---

## G. Module Organization

```typescript
// ✅ Barrel exports for public API of a feature
// features/orders/index.ts
export type { Order, CreateOrderDto } from './domain/order.js';
export { OrderService } from './application/orderService.js';
export { createOrdersRouter } from './adapters/http/ordersRouter.js';

// Consumer imports from the feature barrel
import { OrderService } from '@/features/orders';
// Not from deep internal paths:
import { OrderService } from '@/features/orders/application/orderService'; // ❌
```
