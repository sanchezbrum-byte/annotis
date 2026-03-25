# JavaScript Async Patterns

---

## async/await (Preferred)

Always prefer `async/await` over raw `.then()` chains for readability:

```javascript
// ✅ GOOD: async/await — linear, readable
async function fetchUserOrders(userId) {
  const user = await userRepo.findById(userId);
  if (!user) throw new NotFoundError(`User ${userId} not found`);
  const orders = await orderRepo.findByUserId(userId);
  return { user, orders };
}

// ❌ BAD: nested .then() — callback hell equivalent
function fetchUserOrders(userId) {
  return userRepo.findById(userId)
    .then((user) => {
      if (!user) throw new NotFoundError(`User ${userId} not found`);
      return orderRepo.findByUserId(userId)
        .then((orders) => ({ user, orders }));
    });
}
```

## Parallel Execution

Use `Promise.all` for independent async operations:

```javascript
// ✅ GOOD: run in parallel — total time = max(t1, t2)
async function getDashboardData(userId) {
  const [user, orders, notifications] = await Promise.all([
    userRepo.findById(userId),
    orderRepo.findByUserId(userId),
    notificationService.getUnread(userId),
  ]);
  return { user, orders, notifications };
}

// ❌ BAD: sequential — total time = t1 + t2 + t3
async function getDashboardData(userId) {
  const user = await userRepo.findById(userId);
  const orders = await orderRepo.findByUserId(userId);
  const notifications = await notificationService.getUnread(userId);
  return { user, orders, notifications };
}
```

## Error Handling with async/await

```javascript
// ✅ Wrap risky operations and translate errors
async function processPayment(orderId, cardToken) {
  let order;
  try {
    order = await orderRepo.findById(orderId);
  } catch (dbError) {
    logger.error('Database error fetching order', { orderId, error: dbError.message });
    throw new ServiceUnavailableError('Order service temporarily unavailable');
  }

  if (!order) throw new NotFoundError(`Order ${orderId} not found`);

  try {
    return await paymentGateway.charge(order.total, cardToken);
  } catch (gatewayError) {
    if (gatewayError.isDecline) throw new PaymentDeclinedError(gatewayError.code);
    logger.error('Gateway error', { orderId, error: gatewayError.message });
    throw new PaymentServiceError('Payment service unavailable');
  }
}
```

## Never Mix Callbacks with async/await

```javascript
// ❌ BAD: mixing paradigms
async function readFile(path) {
  return new Promise((resolve, reject) => {
    fs.readFile(path, (err, data) => { // callback inside async function
      if (err) reject(err);
      resolve(data);
    });
  });
}

// ✅ GOOD: use the promisified version
import { readFile } from 'fs/promises';

async function readFile(path) {
  return readFile(path, 'utf-8');
}
```

## Avoid Unhandled Promise Rejections

```javascript
// ❌ BAD: fire-and-forget with no error handling
async function init() {
  loadConfig(); // returns a promise; if it rejects, it's unhandled
}

// ✅ GOOD: always handle or propagate
async function init() {
  await loadConfig(); // rejection propagates to caller
}

// ✅ GOOD: explicit fire-and-forget with error logging
loadConfig().catch((err) => logger.error('Config load failed', { error: err.message }));
```
