/**
 * ❌ BAD EXAMPLE — Do NOT follow this code.
 * Every violation is annotated.
 */

// ❌ BAD: any type throughout — disables all TypeScript type safety
// ❌ BAD: no explicit return types — caller cannot know what to expect
// ❌ BAD: class does too many things (SRP violation)
export class BadNotificationService {
  // ❌ BAD: public mutable state — can be modified by anyone
  public db: any; // ❌ BAD: any type
  public cache: any = {}; // ❌ BAD: any + mutable public cache
  // ❌ BAD: hardcoded secret in class property
  private apiKey = 'nfn_live_secret_key_hardcoded_12345'; // ❌ CRITICAL: hardcoded secret

  // ❌ BAD: constructor takes no dependencies — impossible to test
  constructor() {
    // ❌ BAD: instantiates concrete dependencies inside class (anti-DI)
    this.db = new (require('./database').Database)();
  }

  // ❌ BAD: no return type annotation
  // ❌ BAD: 6 parameters (max is 4) — use an options object
  // ❌ BAD: vague parameter names (u, t, m, s)
  async send(u: any, t: any, m: any, s: any, d: any, f: any) {
    // ❌ BAD: no input validation — trusts caller completely
    // ❌ BAD: catches all errors and returns null — silent failure
    try {
      // ❌ BAD: no-op if condition — undefined behavior
      if (u) {
        if (t) {
          if (m) {
            // ❌ BAD: deep nesting — use early returns instead

            // ❌ BAD: string concatenation for SQL — SQL injection vulnerability
            const user = await this.db.query(
              `SELECT * FROM users WHERE id = '${u}'` // ❌ CRITICAL: SQLi
            );

            // ❌ BAD: accessing property on possibly undefined with no null check
            console.log('user email:', user.email); // ❌ BAD: console.log + potential crash

            // ❌ BAD: no idempotency — will duplicate on retry
            // ❌ BAD: no error handling for HTTP call
            const response = await fetch('https://notifications.internal/send', {
              method: 'POST',
              // ❌ BAD: hardcoded URL (should be config), hardcoded API key
              headers: { 'x-api-key': 'nfn_live_secret_key_hardcoded_12345' },
              body: JSON.stringify({ to: user.email, message: m }),
              // ❌ BAD: no timeout — will hang forever if service is slow
            });

            // ❌ BAD: no response status check — assumes 200
            const data = await response.json();

            // ❌ BAD: mutating shared mutable cache with no TTL
            this.cache[u] = data;

            return data; // ❌ BAD: returns raw API response — leaks internal structure
          }
        }
      }
    } catch (e) {
      // ❌ BAD: catch swallows ALL errors and returns null
      // ❌ BAD: no logging — impossible to debug production failures
      return null;
    }
  }

  // ❌ BAD: function name mixes concerns (does 3 things)
  // ❌ BAD: no return type
  async getAndFormatAndSendDigest(userId: any, type: any) {
    // ❌ BAD: using == instead of === for type comparison
    if (type == 'weekly') { // ❌ BAD: loose equality
      var notifications = await this.db.query( // ❌ BAD: var (not const/let)
        `SELECT * FROM notifications WHERE user_id = ${userId}` // ❌ BAD: SQLi
      );

      // ❌ BAD: string concatenation in loop — O(n²)
      var html = '<html>';
      for (var i = 0; i < notifications.length; i++) {
        html = html + '<p>' + notifications[i].message + '</p>'; // ❌ O(n²) + XSS via .message
      }
      html = html + '</html>';

      // ❌ BAD: calling send() without awaiting it — fire and forget
      this.send(userId, 'email', html, null, null, null); // ❌ no await
    }
  }

  // ❌ BAD: as-assertion to bypass type checking
  getUnsafe(data: unknown) {
    return (data as any).deeplyNested.value; // ❌ BAD: crashes at runtime if structure differs
  }
}
