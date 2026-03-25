# JavaScript Style Guide

> **Sources:** Airbnb JavaScript Style Guide (github.com/airbnb/javascript), Google JavaScript Style Guide (google.github.io/styleguide/jsguide.html), ESLint recommended rules, Prettier defaults

---

## A. Formatting & Style

### Line Length

| Limit | Value | Source |
|-------|-------|--------|
| **Hard limit** | **100 characters** | Airbnb Style Guide (enforced by ESLint `max-len`) |
| **Soft limit** | **80 characters** | Google JS Style Guide |

### Indentation

- **2 spaces** per level — never tabs (Airbnb, Google)
- Configure Prettier: `"tabWidth": 2`

### Semicolons

**Required** at the end of every statement (Airbnb). Prettier enforces this.

```javascript
// ✅ GOOD
const user = getUser(id);
return user;

// ❌ BAD — relying on ASI is error-prone
const user = getUser(id)
return user
```

### Quotes

- **Single quotes** for regular strings: `'hello'`
- **Template literals** for string interpolation: `` `Hello, ${name}!` ``
- Double quotes only in JSX attributes: `<Component prop="value" />`

### Trailing Commas

Use trailing commas in multi-line arrays, objects, function parameters (ES2017+):

```javascript
// ✅ GOOD — cleaner diffs; adding/removing elements changes only one line
const config = {
  host: 'localhost',
  port: 5432,
  ssl: true,
};

function createUser(
  name,
  email,
  role,
) { ... }
```

### Blank Lines

- 1 blank line between function declarations
- 1 blank line between logical sections within a function
- No trailing blank lines inside blocks

### Brace Style

Always use braces — even for single-line blocks (Airbnb):

```javascript
// ❌ BAD
if (condition) doSomething();

// ✅ GOOD
if (condition) {
  doSomething();
}
```

---

## B. Naming Conventions

| Concept | Convention | Example |
|---------|-----------|---------|
| Variables | `camelCase` | `userId`, `totalPrice` |
| Constants (module-level) | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `BASE_URL` |
| Functions | `camelCase` | `calculateTotal`, `getUser` |
| Classes | `PascalCase` | `OrderService`, `PaymentProcessor` |
| Files (modules) | `camelCase` or `kebab-case` | `orderService.js` or `order-service.js` (pick one, be consistent) |
| Private convention | `_camelCase` | `_validateInput` (JS has no true private) |
| Boolean vars | `is/has/can/should` prefix | `isAuthenticated`, `hasPermission` |

### Variable Declarations

```javascript
// ✅ Use const by default
const MAX_RETRIES = 3;
const user = await getUser(id);

// ✅ Use let only when the variable will be reassigned
let retryCount = 0;
retryCount += 1;

// ❌ NEVER use var — function scoping causes bugs
var result = compute(); // forbidden
```

---

## C. Functions & Methods

### Arrow Functions vs Named Functions

```javascript
// ✅ Arrow functions for callbacks and expressions
const doubled = numbers.map((n) => n * 2);
const isEven = (n) => n % 2 === 0;

// ✅ Named function declarations for top-level functions
function processPayment(order, card) {
  // named → better stack traces, hoisted
}

// ✅ Named function expressions for assignment
const calculateTotal = function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
};
```

### Maximum Parameters

**Maximum 4 parameters.** Use an options object for > 4:

```javascript
// ❌ BAD: 6 parameters — impossible to call without looking up the signature
function createOrder(userId, items, currency, discount, shippingAddress, paymentMethod) { }

// ✅ GOOD: options object with destructuring
function createOrder({ userId, items, currency, discount, shippingAddress, paymentMethod }) { }

// Or use a class/factory:
const order = new OrderBuilder()
  .forUser(userId)
  .withItems(items)
  .inCurrency(currency)
  .build();
```

### Early Returns

```javascript
// ❌ BAD: deep nesting
function processOrder(order) {
  if (order) {
    if (order.isValid()) {
      if (order.user.isActive()) {
        return executeOrder(order);
      } else {
        return { error: 'User inactive' };
      }
    } else {
      return { error: 'Invalid order' };
    }
  } else {
    return { error: 'Order not found' };
  }
}

// ✅ GOOD: guard clauses
function processOrder(order) {
  if (!order) return { error: 'Order not found' };
  if (!order.isValid()) return { error: 'Invalid order' };
  if (!order.user.isActive()) return { error: 'User inactive' };
  return executeOrder(order);
}
```

### Pure Functions

Prefer pure functions (no side effects, deterministic output):

```javascript
// ✅ Pure — same inputs always produce same output
function applyDiscount(price, discountRate) {
  return price * (1 - discountRate);
}

// ❌ Impure — depends on external state
function applyDiscount(price) {
  return price * (1 - currentPromotion.rate); // currentPromotion is external
}
```

---

## D. Comments & Documentation

### JSDoc for Public APIs

```javascript
/**
 * Calculate the total price for an order after applying a discount.
 *
 * @param {Object} order - The order object containing items.
 * @param {Array<{price: number, quantity: number}>} order.items - Line items.
 * @param {number} discountRate - Discount as a decimal (0.10 = 10% off). Must be 0–1.
 * @returns {number} Total price after discount, rounded to 2 decimal places.
 * @throws {RangeError} If discountRate is outside the 0–1 range.
 *
 * @example
 * const total = calculateOrderTotal(order, 0.10);
 * // => 90.00 for a $100 order with 10% discount
 */
function calculateOrderTotal(order, discountRate) {
  if (discountRate < 0 || discountRate > 1) {
    throw new RangeError(`discountRate must be 0–1, got: ${discountRate}`);
  }
  const subtotal = order.items.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0,
  );
  return Math.round(subtotal * (1 - discountRate) * 100) / 100;
}
```

### Inline Comments — WHY not WHAT

```javascript
// ✅ GOOD — explains non-obvious reasoning
// Stripe requires idempotency keys scoped to a 24-hour window.
// Using date-based key ensures retries on the same day are deduplicated.
const idempotencyKey = `pay:${orderId}:${new Date().toISOString().slice(0, 10)}`;

// ❌ BAD — narrates what the code already says
// Increment retry count
retryCount += 1;
```

### TODO/FIXME

```javascript
// TODO(alice@example.com, 2025-03-15, INFRA-423): Replace with async client
// once Node.js 22 is stable in production.
const result = syncClient.fetch(url);

// FIXME(bob@example.com, 2025-02-01, PAY-887): Integer overflow for large amounts.
```

---

## E. Error Handling

```javascript
// ✅ GOOD: specific error handling with context
async function chargeCard(orderId, cardToken, amount) {
  try {
    return await stripe.charges.create({ amount, source: cardToken });
  } catch (error) {
    if (error.type === 'StripeCardError') {
      logger.info('Card declined', { orderId, code: error.code });
      throw new PaymentDeclinedError(error.code);
    }
    logger.error('Stripe API error', { orderId, error: error.message });
    throw new PaymentServiceError('Payment service unavailable');
  }
}

// ❌ BAD: swallowing errors
async function chargeCard(orderId, cardToken, amount) {
  try {
    return await stripe.charges.create({ amount, source: cardToken });
  } catch (e) {
    return null; // caller cannot tell if payment succeeded or failed
  }
}
```

### Never Throw Non-Error Objects

```javascript
// ❌ BAD
throw 'Payment failed';
throw { code: 500, message: 'Error' };

// ✅ GOOD
throw new PaymentError('Payment failed');
throw new Error('Unexpected state');
```

---

## F. Modern JS Patterns

### Destructuring

```javascript
// ✅ Object destructuring
const { id, name, email } = user;
function greet({ name, greeting = 'Hello' }) {
  return `${greeting}, ${name}!`;
}

// ✅ Array destructuring
const [first, second, ...rest] = items;
const [error, result] = await safeAsync(riskyOperation());
```

### Spread / Rest

```javascript
// ✅ Safe object merging (no mutation)
const updated = { ...defaultConfig, ...userConfig };

// ✅ Rest params instead of arguments
function sum(...numbers) {
  return numbers.reduce((total, n) => total + n, 0);
}
```

### Optional Chaining and Nullish Coalescing

```javascript
// ✅ Safe property access
const city = user?.address?.city ?? 'Unknown';
const count = data?.items?.length ?? 0;
```

---

## G. Module System

Use **ES Modules** (import/export) for new code. CommonJS (`require`) only for legacy Node.js code that cannot be migrated:

```javascript
// ✅ ES Modules (preferred)
import { calculateTotal } from './orderUtils.js';
export function processOrder(order) { ... }
export default class OrderService { ... }

// Legacy CommonJS (only when required)
const { calculateTotal } = require('./orderUtils');
module.exports = { processOrder };
```

---

## H. Security

### No eval / new Function

```javascript
// ❌ EXTREMELY DANGEROUS — arbitrary code execution
eval(userInput);
new Function('return ' + userInput)();

// ✅ GOOD: use JSON.parse for data, not eval
const data = JSON.parse(userInput);
```

### Prototype Pollution Prevention

```javascript
// ❌ BAD: merging user-controlled object
Object.assign(target, userControlledObject);

// ✅ GOOD: use a safe merge that rejects prototype properties
function safeMerge(target, source) {
  for (const key of Object.keys(source)) {
    if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
      continue; // reject prototype-polluting keys
    }
    target[key] = source[key];
  }
  return target;
}
```
