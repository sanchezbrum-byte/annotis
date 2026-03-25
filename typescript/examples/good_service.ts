/**
 * User notification service — demonstrates clean TypeScript patterns.
 *
 * Features demonstrated:
 * - Discriminated union for notification types
 * - Branded types for IDs
 * - Dependency injection
 * - Explicit return types
 * - Zod validation at boundary
 * - Result type for expected failures
 */

import { z } from 'zod';

// ---------------------------------------------------------------------------
// Branded types — prevent mixing up IDs at compile time
// ---------------------------------------------------------------------------

type UserId = string & { readonly __brand: 'UserId' };
type NotificationId = string & { readonly __brand: 'NotificationId' };

function asUserId(id: string): UserId {
  return id as UserId;
}

// ---------------------------------------------------------------------------
// Domain types
// ---------------------------------------------------------------------------

// ✅ Discriminated union — exhaustive, type-safe switching
type NotificationPayload =
  | { type: 'order_confirmed'; orderId: string; total: number; currency: string }
  | { type: 'payment_failed'; orderId: string; reason: string }
  | { type: 'shipping_update'; orderId: string; trackingNumber: string; eta: Date }
  | { type: 'account_alert'; message: string; severity: 'info' | 'warning' | 'critical' };

interface Notification {
  readonly id: NotificationId;
  readonly userId: UserId;
  readonly payload: NotificationPayload;
  readonly createdAt: Date;
  readonly readAt: Date | null;
}

// ✅ Result type — explicit error handling without exceptions for expected cases
type Result<T, E = Error> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

// ---------------------------------------------------------------------------
// Validation schema (Zod) — single source of truth for input validation
// ---------------------------------------------------------------------------

const SendNotificationSchema = z.object({
  userId: z.string().min(1, 'userId is required'),
  payload: z.discriminatedUnion('type', [
    z.object({
      type: z.literal('order_confirmed'),
      orderId: z.string(),
      total: z.number().positive(),
      currency: z.enum(['USD', 'EUR', 'GBP']),
    }),
    z.object({
      type: z.literal('payment_failed'),
      orderId: z.string(),
      reason: z.string(),
    }),
    z.object({
      type: z.literal('shipping_update'),
      orderId: z.string(),
      trackingNumber: z.string(),
      eta: z.coerce.date(),
    }),
    z.object({
      type: z.literal('account_alert'),
      message: z.string().min(1).max(500),
      severity: z.enum(['info', 'warning', 'critical']),
    }),
  ]),
});

type SendNotificationInput = z.infer<typeof SendNotificationSchema>;

// ---------------------------------------------------------------------------
// Ports (interfaces for dependency injection)
// ---------------------------------------------------------------------------

interface NotificationRepository {
  save(notification: Notification): Promise<Notification>;
  findByUserId(userId: UserId, limit?: number): Promise<Notification[]>;
  markAsRead(id: NotificationId, userId: UserId): Promise<Notification | null>;
}

interface NotificationChannel {
  send(notification: Notification): Promise<void>;
}

interface Logger {
  info(message: string, context?: Record<string, unknown>): void;
  error(message: string, context?: Record<string, unknown>): void;
}

// ---------------------------------------------------------------------------
// Service implementation
// ---------------------------------------------------------------------------

export class NotificationService {
  constructor(
    private readonly repo: NotificationRepository,
    private readonly channel: NotificationChannel,
    private readonly logger: Logger,
  ) {}

  /**
   * Send a notification to a user.
   *
   * Validates input, persists the notification, and delivers via configured channel.
   *
   * @param input - Raw, unvalidated notification request.
   * @returns Result with the created notification, or validation error.
   */
  async send(input: unknown): Promise<Result<Notification, Error>> {
    // ✅ Validate at boundary with Zod
    const parsed = SendNotificationSchema.safeParse(input);
    if (!parsed.success) {
      return { ok: false, error: new Error(parsed.error.message) };
    }

    const { userId, payload } = parsed.data;
    const notification: Notification = {
      id: generateId() as NotificationId,
      userId: asUserId(userId),
      payload,
      createdAt: new Date(),
      readAt: null,
    };

    try {
      const saved = await this.repo.save(notification);

      // Deliver async — do not fail the save if delivery fails
      this.channel.send(saved).catch((err: Error) => {
        this.logger.error('Failed to deliver notification', {
          notificationId: saved.id,
          error: err.message,
        });
      });

      this.logger.info('Notification sent', {
        notificationId: saved.id,
        userId,
        type: payload.type,
      });

      return { ok: true, value: saved };
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      this.logger.error('Failed to save notification', {
        userId,
        error: error.message,
      });
      return { ok: false, error };
    }
  }

  /**
   * Get unread notifications for a user.
   *
   * @param userId - The user whose notifications to retrieve.
   * @param limit - Maximum number to return. Defaults to 20.
   * @returns Array of notifications, most recent first.
   */
  async getUnread(userId: UserId, limit = 20): Promise<Notification[]> {
    const all = await this.repo.findByUserId(userId, limit);
    return all.filter((n) => n.readAt === null);
  }

  /**
   * Format a notification payload into a human-readable string.
   *
   * This is a pure function — it has no side effects and is deterministic.
   * ✅ Exhaustive switch — TypeScript will error if a new type is added without handling it.
   */
  formatMessage(payload: NotificationPayload): string {
    switch (payload.type) {
      case 'order_confirmed':
        return `Your order has been confirmed. Total: ${payload.currency} ${payload.total}`;
      case 'payment_failed':
        return `Payment failed for your order: ${payload.reason}`;
      case 'shipping_update':
        return `Your order is on its way! Tracking: ${payload.trackingNumber}. ETA: ${payload.eta.toDateString()}`;
      case 'account_alert':
        return `[${payload.severity.toUpperCase()}] ${payload.message}`;
      default: {
        // ✅ TypeScript exhaustiveness check
        const _exhaustive: never = payload;
        throw new Error(`Unknown notification type: ${JSON.stringify(_exhaustive)}`);
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function generateId(): string {
  return crypto.randomUUID();
}
