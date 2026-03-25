# JavaScript AI Rules

> Full reference: `javascript/style-guide.md`

---

## Formatting (Airbnb + Prettier)

- Hard line limit: **100 chars** (Airbnb)
- Indentation: **2 spaces**
- Semicolons: **required**
- Quotes: **single** (`'string'`), backticks for templates
- Trailing commas: required in multi-line
- Always use braces even for single-line `if`

## Variables

```javascript
const MAX_RETRIES = 3;          // ✅ const by default
let retryCount = 0;             // ✅ let when reassigned
// var — FORBIDDEN (no-var ESLint rule)
```

## Naming

| Concept | Style | Example |
|---------|-------|---------|
| Variables/functions | `camelCase` | `getUser`, `totalPrice` |
| Classes | `PascalCase` | `OrderService` |
| Constants (module-level) | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Files | `camelCase` or `kebab-case` | `orderService.js` |
| Booleans | `is/has/can/should` | `isAuthenticated` |

## Functions

- Max **4 parameters** — use options object for more
- Prefer arrow functions for callbacks; named functions for top-level
- Early returns over deep nesting
- `async/await` over `.then()` chains
- `Promise.all()` for parallel independent async operations

## Error Handling

```javascript
// ✅ Specific error types, logged, translated
try {
  return await stripe.charges.create({ amount, source: token });
} catch (error) {
  if (error.type === 'StripeCardError') {
    logger.info('Card declined', { orderId, code: error.code });
    throw new PaymentDeclinedError(error.code);
  }
  logger.error('Stripe error', { orderId, error: error.message });
  throw new PaymentServiceError('Service unavailable');
}

// ❌ Never throw non-Error objects
throw 'Payment failed';  // BAD — always: throw new Error(...)
```

## Security

```javascript
// ❌ CRITICAL: never eval user input
eval(userInput);           // arbitrary code execution

// ✅ SQL: use parameterized queries
db.query('SELECT * FROM users WHERE email = $1', [email]);

// ✅ Secrets: from process.env only
const apiKey = process.env.STRIPE_API_KEY;
```

## ES Module Imports

```javascript
// ✅ ES Modules (preferred)
import { calculateTotal } from './utils.js';
export function processOrder(order) { ... }

// CommonJS only for legacy code
const { processOrder } = require('./orderService');
```

## Tooling

```bash
eslint . --fix        # lint
prettier --write .    # format
jest --coverage       # test
npm audit             # security scan
```
