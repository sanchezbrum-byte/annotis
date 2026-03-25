# JavaScript Testing Standards

> **Tools:** Jest, Supertest (API integration tests), MSW (Mock Service Worker for HTTP mocking)

---

## Jest Configuration

```json
// jest.config.cjs
module.exports = {
  testEnvironment: 'node',
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/**/index.js',
    '!src/db/migrations/**',
  ],
  coverageThresholds: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  testMatch: ['**/*.test.js'],
};
```

## Test Naming

```javascript
describe('calculateOrderTotal', () => {
  it('returns zero for an empty items array');
  it('sums item prices correctly');
  it('applies percentage discount');
  it('throws RangeError when discountRate > 1');
});

describe('OrderService', () => {
  describe('createOrder', () => {
    it('creates and returns a new order for a valid request');
    it('publishes OrderCreated event after saving');
    it('throws ValidationError when items array is empty');
  });
});
```

## AAA Pattern in Jest

```javascript
describe('processPayment', () => {
  it('returns payment confirmation when charge succeeds', async () => {
    // Arrange
    const mockGateway = { charge: jest.fn().mockResolvedValue({ id: 'pay_123' }) };
    const service = createPaymentService({ gateway: mockGateway });
    const order = buildOrder({ total: 100 });

    // Act
    const result = await service.processPayment(order, 'tok_visa');

    // Assert
    expect(result.paymentId).toBe('pay_123');
    expect(mockGateway.charge).toHaveBeenCalledWith({
      amount: 100,
      source: 'tok_visa',
    });
  });
});
```

## API Integration Tests with Supertest

```javascript
import request from 'supertest';
import { createApp } from '../../src/app.js';

describe('POST /orders', () => {
  let app;
  beforeAll(async () => {
    app = await createApp({ db: testDb });
  });

  it('returns 201 with order ID for valid request', async () => {
    const response = await request(app)
      .post('/orders')
      .set('Authorization', `Bearer ${validToken}`)
      .send({ items: [{ productId: 'p1', quantity: 2 }], currency: 'USD' });

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');
  });

  it('returns 422 for empty items array', async () => {
    const response = await request(app)
      .post('/orders')
      .set('Authorization', `Bearer ${validToken}`)
      .send({ items: [], currency: 'USD' });

    expect(response.status).toBe(422);
  });
});
```
