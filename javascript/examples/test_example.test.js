/**
 * Tests for createOrderService — demonstrates Jest best practices.
 *
 * Patterns:
 * - AAA (Arrange-Act-Assert) in every test
 * - Factory functions for test data (not magic literals)
 * - Dependency injection for mocks (not jest.mock() of modules)
 * - Descriptive test names: <method> <scenario> <expected behavior>
 */

import { createOrderService } from '../good_module.js';
import { OrderNotFoundError, PaymentDeclinedError, ValidationError } from '../../errors/index.js';

// ---------------------------------------------------------------------------
// Test data factories
// ---------------------------------------------------------------------------

function buildOrderItem(overrides = {}) {
  return {
    productId: 'prod-001',
    quantity: 1,
    unitPrice: 50.00,
    ...overrides,
  };
}

function buildOrder(overrides = {}) {
  return {
    id: 'order-123',
    userId: 'user-456',
    total: 100.00,
    currency: 'USD',
    status: 'pending',
    items: [buildOrderItem()],
    ...overrides,
  };
}

function buildCreateOrderParams(overrides = {}) {
  return {
    userId: 'user-456',
    items: [buildOrderItem({ quantity: 2, unitPrice: 50.00 })],
    currency: 'USD',
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Mock factories
// ---------------------------------------------------------------------------

function buildMockOrderRepo(overrides = {}) {
  return {
    create: jest.fn().mockResolvedValue(buildOrder()),
    findById: jest.fn().mockResolvedValue(buildOrder()),
    update: jest.fn().mockResolvedValue(undefined),
    ...overrides,
  };
}

function buildMockPaymentGateway(overrides = {}) {
  return {
    charge: jest.fn().mockResolvedValue({ id: 'pay-789', status: 'succeeded' }),
    ...overrides,
  };
}

function buildMockEventBus() {
  return { publish: jest.fn().mockResolvedValue(undefined) };
}

function buildMockLogger() {
  return { info: jest.fn(), error: jest.fn(), warn: jest.fn() };
}

function buildService(overrides = {}) {
  return createOrderService({
    orderRepo: buildMockOrderRepo(),
    paymentGateway: buildMockPaymentGateway(),
    eventBus: buildMockEventBus(),
    logger: buildMockLogger(),
    ...overrides,
  });
}

// ---------------------------------------------------------------------------
// createOrder tests
// ---------------------------------------------------------------------------

describe('createOrder', () => {
  it('returns the created order for valid input', async () => {
    // Arrange
    const expectedOrder = buildOrder({ id: 'new-order-1' });
    const orderRepo = buildMockOrderRepo({ create: jest.fn().mockResolvedValue(expectedOrder) });
    const service = buildService({ orderRepo });

    // Act
    const result = await service.createOrder(buildCreateOrderParams());

    // Assert
    expect(result.id).toBe('new-order-1');
  });

  it('persists order with correct total calculated from items', async () => {
    // Arrange
    const orderRepo = buildMockOrderRepo();
    const service = buildService({ orderRepo });
    const params = buildCreateOrderParams({
      items: [
        buildOrderItem({ quantity: 2, unitPrice: 30.00 }),
        buildOrderItem({ quantity: 1, unitPrice: 40.00 }),
      ],
    });

    // Act
    await service.createOrder(params);

    // Assert — total = (2 * 30) + (1 * 40) = 100
    expect(orderRepo.create).toHaveBeenCalledWith(
      expect.objectContaining({ total: 100.00 }),
    );
  });

  it('publishes order.created event after creating order', async () => {
    // Arrange
    const eventBus = buildMockEventBus();
    const service = buildService({ eventBus });

    // Act
    await service.createOrder(buildCreateOrderParams());

    // Assert
    expect(eventBus.publish).toHaveBeenCalledWith(
      'order.created',
      expect.objectContaining({ userId: 'user-456' }),
    );
  });

  // Corner cases
  it('throws ValidationError when items array is empty', async () => {
    const service = buildService();
    await expect(
      service.createOrder(buildCreateOrderParams({ items: [] })),
    ).rejects.toThrow(ValidationError);
  });

  it('throws ValidationError when currency is unsupported', async () => {
    const service = buildService();
    await expect(
      service.createOrder(buildCreateOrderParams({ currency: 'XYZ' })),
    ).rejects.toThrow(ValidationError);
  });

  it('throws ValidationError when userId is missing', async () => {
    const service = buildService();
    await expect(
      service.createOrder(buildCreateOrderParams({ userId: '' })),
    ).rejects.toThrow(ValidationError);
  });

  it('throws ValidationError when items exceed maximum count', async () => {
    const service = buildService();
    const tooManyItems = Array.from({ length: 101 }, () => buildOrderItem());
    await expect(
      service.createOrder(buildCreateOrderParams({ items: tooManyItems })),
    ).rejects.toThrow(ValidationError);
  });
});

// ---------------------------------------------------------------------------
// processPayment tests
// ---------------------------------------------------------------------------

describe('processPayment', () => {
  it('returns payment confirmation when charge succeeds', async () => {
    // Arrange
    const paymentGateway = buildMockPaymentGateway({
      charge: jest.fn().mockResolvedValue({ id: 'pay-999' }),
    });
    const service = buildService({ paymentGateway });

    // Act
    const result = await service.processPayment('order-123', 'tok_visa');

    // Assert
    expect(result.paymentId).toBe('pay-999');
    expect(result.status).toBe('paid');
  });

  it('throws OrderNotFoundError when order does not exist', async () => {
    const orderRepo = buildMockOrderRepo({ findById: jest.fn().mockResolvedValue(null) });
    const service = buildService({ orderRepo });

    await expect(service.processPayment('nonexistent', 'tok_visa'))
      .rejects.toThrow(OrderNotFoundError);
  });

  it('throws ValidationError when order is already paid', async () => {
    const orderRepo = buildMockOrderRepo({
      findById: jest.fn().mockResolvedValue(buildOrder({ status: 'paid' })),
    });
    const service = buildService({ orderRepo });

    await expect(service.processPayment('order-123', 'tok_visa'))
      .rejects.toThrow(ValidationError);
  });

  it('throws PaymentDeclinedError when gateway declines card', async () => {
    const declineError = new Error('Card declined');
    declineError.isDecline = true;
    declineError.code = 'insufficient_funds';

    const paymentGateway = buildMockPaymentGateway({
      charge: jest.fn().mockRejectedValue(declineError),
    });
    const service = buildService({ paymentGateway });

    await expect(service.processPayment('order-123', 'tok_declined'))
      .rejects.toThrow(PaymentDeclinedError);
  });

  it('does not update order status when gateway fails', async () => {
    const orderRepo = buildMockOrderRepo();
    const paymentGateway = buildMockPaymentGateway({
      charge: jest.fn().mockRejectedValue(new Error('Connection refused')),
    });
    const service = buildService({ orderRepo, paymentGateway });

    await expect(service.processPayment('order-123', 'tok_visa')).rejects.toThrow();

    // Assert: order NOT updated on failure (data integrity)
    expect(orderRepo.update).not.toHaveBeenCalled();
  });
});
