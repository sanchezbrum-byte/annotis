/**
 * @fileoverview Order service — demonstrates clean JavaScript style.
 *
 * Implements business logic for order creation and payment processing,
 * following Single Responsibility, dependency injection, and proper
 * async/await patterns.
 */

'use strict';

import { OrderNotFoundError, PaymentDeclinedError, ValidationError } from '../errors/index.js';

const SUPPORTED_CURRENCIES = new Set(['USD', 'EUR', 'GBP']);
const MAX_ITEMS_PER_ORDER = 100;

/**
 * Create an order service with injected dependencies.
 *
 * @param {Object} deps - Service dependencies.
 * @param {Object} deps.orderRepo - Order repository for persistence.
 * @param {Object} deps.paymentGateway - Payment processor adapter.
 * @param {Object} deps.eventBus - Domain event publisher.
 * @param {Object} deps.logger - Structured logger.
 * @returns {Object} Order service with createOrder and cancelOrder methods.
 */
export function createOrderService({ orderRepo, paymentGateway, eventBus, logger }) {
  return { createOrder, cancelOrder, processPayment };

  /**
   * Create a new order for a user.
   *
   * @param {Object} params - Order creation parameters.
   * @param {string} params.userId - ID of the user placing the order.
   * @param {Array<{productId: string, quantity: number, unitPrice: number}>} params.items
   * @param {string} params.currency - ISO 4217 currency code.
   * @returns {Promise<{id: string, total: number, status: string}>} Created order.
   * @throws {ValidationError} If input is invalid.
   */
  async function createOrder({ userId, items, currency }) {
    // ✅ Validate at boundary before any side effects
    validateCreateOrderInput({ userId, items, currency });

    const total = calculateTotal(items);

    logger.info('Creating order', { userId, itemCount: items.length, total, currency });

    const order = await orderRepo.create({
      userId,
      items,
      total,
      currency,
      status: 'pending',
    });

    // ✅ Publish domain event after successful persistence
    await eventBus.publish('order.created', {
      orderId: order.id,
      userId,
      total,
      currency,
    });

    logger.info('Order created', { orderId: order.id, userId });
    return order;
  }

  /**
   * Process payment for an existing pending order.
   *
   * @param {string} orderId - ID of the order to pay.
   * @param {string} cardToken - Tokenized card from payment provider.
   * @returns {Promise<{orderId: string, paymentId: string, status: string}>}
   * @throws {OrderNotFoundError} If order does not exist.
   * @throws {PaymentDeclinedError} If the card is declined.
   */
  async function processPayment(orderId, cardToken) {
    const order = await orderRepo.findById(orderId);

    // ✅ Early return guard — clear error at the right level
    if (!order) {
      throw new OrderNotFoundError(orderId);
    }

    if (order.status !== 'pending') {
      throw new ValidationError(`Order ${orderId} is not payable (status: ${order.status})`);
    }

    // ✅ Idempotency key prevents double-charges on retry
    // Stripe deduplication window is 24h, so date-scoped key is sufficient.
    const idempotencyKey = buildIdempotencyKey(orderId);

    let payment;
    try {
      payment = await paymentGateway.charge({
        amount: order.total,
        currency: order.currency,
        source: cardToken,
        idempotencyKey,
      });
    } catch (error) {
      if (error.isDecline) {
        logger.info('Payment declined', { orderId, declineCode: error.code });
        throw new PaymentDeclinedError(error.code);
      }
      logger.error('Payment gateway error', { orderId, error: error.message });
      throw new Error('Payment service temporarily unavailable');
    }

    await orderRepo.update(orderId, { status: 'paid', paymentId: payment.id });
    await eventBus.publish('payment.completed', { orderId, paymentId: payment.id });

    return { orderId, paymentId: payment.id, status: 'paid' };
  }

  /**
   * Cancel a pending order.
   *
   * @param {string} orderId - ID of the order to cancel.
   * @param {string} userId - ID of the user requesting cancellation.
   * @returns {Promise<void>}
   */
  async function cancelOrder(orderId, userId) {
    const order = await orderRepo.findById(orderId);
    if (!order) throw new OrderNotFoundError(orderId);
    if (order.userId !== userId) throw new ValidationError('Unauthorized');
    if (order.status !== 'pending') {
      throw new ValidationError(`Cannot cancel order in status: ${order.status}`);
    }

    await orderRepo.update(orderId, { status: 'cancelled' });
    await eventBus.publish('order.cancelled', { orderId, userId });
  }
}

// ---------------------------------------------------------------------------
// Private helpers (module scope, not exported)
// ---------------------------------------------------------------------------

/**
 * Validate create order input parameters.
 *
 * @param {Object} params
 * @throws {ValidationError} On any invalid input.
 */
function validateCreateOrderInput({ userId, items, currency }) {
  if (!userId || typeof userId !== 'string') {
    throw new ValidationError('userId is required and must be a string');
  }
  if (!Array.isArray(items) || items.length === 0) {
    throw new ValidationError('items must be a non-empty array');
  }
  if (items.length > MAX_ITEMS_PER_ORDER) {
    throw new ValidationError(`Cannot exceed ${MAX_ITEMS_PER_ORDER} items per order`);
  }
  if (!SUPPORTED_CURRENCIES.has(currency)) {
    throw new ValidationError(`Unsupported currency: ${currency}`);
  }
}

/**
 * Calculate total price from order items.
 *
 * Time: O(n) where n = number of items.
 *
 * @param {Array<{unitPrice: number, quantity: number}>} items
 * @returns {number} Total price.
 */
function calculateTotal(items) {
  return items.reduce((total, item) => total + item.unitPrice * item.quantity, 0);
}

/**
 * Build a date-scoped idempotency key for payment charges.
 *
 * @param {string} orderId
 * @returns {string}
 */
function buildIdempotencyKey(orderId) {
  const date = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
  return `pay:${orderId}:${date}`;
}
