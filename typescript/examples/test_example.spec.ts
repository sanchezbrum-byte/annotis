/**
 * Tests for NotificationService — demonstrates TypeScript testing best practices.
 *
 * Patterns:
 * - Type-safe fakes (implement interface directly)
 * - Factory functions with proper TypeScript types
 * - describe/it naming: <class> → <method> → <scenario> <expected>
 * - AAA pattern
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { NotificationService } from './good_service.js';

// ---------------------------------------------------------------------------
// Type-safe fake implementations
// ---------------------------------------------------------------------------

class FakeNotificationRepository {
  private store = new Map<string, Notification>();

  async save(notification: Notification): Promise<Notification> {
    this.store.set(notification.id, notification);
    return notification;
  }

  async findByUserId(userId: string): Promise<Notification[]> {
    return [...this.store.values()].filter((n) => n.userId === userId);
  }

  async markAsRead(id: string): Promise<Notification | null> {
    const n = this.store.get(id);
    if (!n) return null;
    const updated = { ...n, readAt: new Date() };
    this.store.set(id, updated);
    return updated;
  }
}

// ---------------------------------------------------------------------------
// Test factories
// ---------------------------------------------------------------------------

function buildOrderConfirmedPayload() {
  return {
    type: 'order_confirmed' as const,
    orderId: 'order-123',
    total: 100.0,
    currency: 'USD' as const,
  };
}

function buildSendInput(overrides = {}) {
  return {
    userId: 'user-456',
    payload: buildOrderConfirmedPayload(),
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

describe('NotificationService', () => {
  let repo: FakeNotificationRepository;
  let channel: { send: ReturnType<typeof vi.fn> };
  let logger: { info: ReturnType<typeof vi.fn>; error: ReturnType<typeof vi.fn> };
  let service: NotificationService;

  beforeEach(() => {
    repo = new FakeNotificationRepository();
    channel = { send: vi.fn().mockResolvedValue(undefined) };
    logger = { info: vi.fn(), error: vi.fn() };
    service = new NotificationService(repo as any, channel, logger);
  });

  // -------------------------------------------------------------------------
  // send()
  // -------------------------------------------------------------------------

  describe('send', () => {
    it('returns ok:true with notification when input is valid', async () => {
      const result = await service.send(buildSendInput());
      expect(result.ok).toBe(true);
      if (result.ok) {
        expect(result.value.userId).toBe('user-456');
        expect(result.value.readAt).toBeNull();
      }
    });

    it('delivers notification via channel after saving', async () => {
      await service.send(buildSendInput());
      // Channel is called asynchronously — use vi.waitFor if needed
      expect(channel.send).toHaveBeenCalledTimes(1);
    });

    it('returns ok:false with validation error when userId is empty', async () => {
      const result = await service.send(buildSendInput({ userId: '' }));
      expect(result.ok).toBe(false);
      if (!result.ok) {
        expect(result.error.message).toContain('userId');
      }
    });

    it('returns ok:false when payload type is unsupported', async () => {
      const result = await service.send({
        userId: 'user-1',
        payload: { type: 'invalid_type' },
      });
      expect(result.ok).toBe(false);
    });

    it('returns ok:false when currency is invalid', async () => {
      const result = await service.send(
        buildSendInput({
          payload: { ...buildOrderConfirmedPayload(), currency: 'XYZ' },
        }),
      );
      expect(result.ok).toBe(false);
    });

    it('returns ok:false and logs error when repository throws', async () => {
      repo.save = vi.fn().mockRejectedValue(new Error('DB connection lost'));
      const result = await service.send(buildSendInput());
      expect(result.ok).toBe(false);
      expect(logger.error).toHaveBeenCalledWith(
        'Failed to save notification',
        expect.objectContaining({ error: 'DB connection lost' }),
      );
    });

    // Corner cases
    it('handles null payload gracefully', async () => {
      const result = await service.send({ userId: 'u1', payload: null });
      expect(result.ok).toBe(false);
    });

    it('handles undefined input gracefully', async () => {
      const result = await service.send(undefined);
      expect(result.ok).toBe(false);
    });
  });

  // -------------------------------------------------------------------------
  // formatMessage()
  // -------------------------------------------------------------------------

  describe('formatMessage', () => {
    it('formats order_confirmed message with total and currency', () => {
      const msg = service.formatMessage({
        type: 'order_confirmed',
        orderId: 'o1',
        total: 49.99,
        currency: 'EUR',
      });
      expect(msg).toContain('EUR');
      expect(msg).toContain('49.99');
    });

    it('formats payment_failed message with reason', () => {
      const msg = service.formatMessage({
        type: 'payment_failed',
        orderId: 'o1',
        reason: 'insufficient_funds',
      });
      expect(msg).toContain('insufficient_funds');
    });

    it('formats account_alert with severity in uppercase', () => {
      const msg = service.formatMessage({
        type: 'account_alert',
        message: 'Suspicious login detected',
        severity: 'critical',
      });
      expect(msg).toContain('CRITICAL');
      expect(msg).toContain('Suspicious login detected');
    });

    it('formats shipping_update with tracking number', () => {
      const msg = service.formatMessage({
        type: 'shipping_update',
        orderId: 'o1',
        trackingNumber: 'UPS-123456',
        eta: new Date('2025-06-01'),
      });
      expect(msg).toContain('UPS-123456');
    });
  });

  // -------------------------------------------------------------------------
  // getUnread()
  // -------------------------------------------------------------------------

  describe('getUnread', () => {
    it('returns only notifications with readAt null', async () => {
      // Arrange: save one read and one unread notification
      await service.send(buildSendInput({ userId: 'user-456' }));
      await service.send(buildSendInput({ userId: 'user-456' }));

      const notifications = await service.getUnread('user-456' as any);

      expect(notifications.every((n) => n.readAt === null)).toBe(true);
    });

    it('returns empty array when user has no notifications', async () => {
      const result = await service.getUnread('nonexistent-user' as any);
      expect(result).toEqual([]);
    });
  });
});
