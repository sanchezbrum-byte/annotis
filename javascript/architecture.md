# JavaScript Architecture

## Node.js Project Structure

```
src/
  features/
    orders/
      ordersRouter.js       # Express/Fastify router
      ordersController.js   # HTTP handlers (request/response)
      ordersService.js      # Business logic
      ordersRepository.js   # Data access
      ordersValidator.js    # Input validation (Zod/Joi)
    users/
      ...
  shared/
    middleware/
      auth.js
      errorHandler.js
      requestLogger.js
    config/
      index.js              # Loads from env vars
    errors/
      AppError.js
      DomainError.js
    db/
      connection.js
      migrations/
  app.js                    # Express app factory (no listen() call)
  server.js                 # Entry point: creates app, starts server
tests/
  unit/
  integration/
  e2e/
package.json
.eslintrc.cjs
prettier.config.cjs
```

## Layer Rules

```javascript
// ✅ GOOD: Controller only handles HTTP concerns
// ordersController.js
async function createOrder(req, res, next) {
  try {
    const validated = createOrderSchema.parse(req.body); // validate at boundary
    const order = await ordersService.createOrder(validated, req.user.id);
    return res.status(201).json(order);
  } catch (error) {
    next(error); // delegate error handling to middleware
  }
}

// ❌ BAD: Business logic in controller
async function createOrder(req, res) {
  const { items, currency } = req.body;
  if (items.length === 0) return res.status(400).json({ error: 'No items' });
  const total = items.reduce((s, i) => s + i.price * i.qty, 0);
  if (total > req.user.creditLimit) return res.status(402).json({ error: 'Over limit' });
  // ... all business logic here (wrong layer)
}
```

## Dependency Injection Pattern

```javascript
// ✅ Factory function pattern for DI
function createOrdersService({ orderRepo, paymentGateway, eventBus }) {
  return {
    async createOrder(data, userId) { ... },
    async cancelOrder(orderId, userId) { ... },
  };
}

// Wire in app.js
const ordersRepo = createOrdersRepository({ db: pool });
const ordersService = createOrdersService({
  orderRepo: ordersRepo,
  paymentGateway: stripeGateway,
  eventBus: kafkaEventBus,
});
```
