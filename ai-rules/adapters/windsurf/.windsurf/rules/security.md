# Security AI Rules

> Full reference: `universal/security.md`

---

## OWASP Top 10:2021 — Quick Reference

| # | Vulnerability | Prevention |
|---|--------------|-----------|
| A01 | Broken Access Control | Check authorization on every data access, not just auth |
| A02 | Cryptographic Failures | TLS 1.2+, bcrypt/Argon2 for passwords, AES-256 at rest |
| A03 | Injection | Parameterized queries, `never` string concatenation in SQL |
| A04 | Insecure Design | Threat model new features handling sensitive data |
| A05 | Security Misconfiguration | No default passwords, disable unused features, hide errors |
| A06 | Vulnerable Components | `npm audit`, `pip-audit`, `cargo audit` in CI |
| A07 | Auth Failures | Rate limiting on auth, MFA, strong session management |
| A08 | Software Integrity | Verify package checksums, sign artifacts |
| A09 | Logging Failures | Log auth events, failures; never log secrets/PII |
| A10 | SSRF | Allowlist for server-side HTTP requests |

---

## Non-Negotiable Rules

### Secrets

```python
# ❌ CRITICAL: never hardcode
API_KEY = "sk_live_hardcoded_abc123"

# ✅ Always from environment or secret manager
API_KEY = os.environ["STRIPE_API_KEY"]
```

### SQL Injection

```python
# ❌ CRITICAL: string concatenation
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ Parameterized
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

### Authentication

```python
# ❌ Trusting user-supplied ID
@router.get("/orders/{order_id}")
def get_order(order_id: str, user_id: str = Body(...)):

# ✅ User identity from validated JWT/session
@router.get("/orders/{order_id}")
def get_order(order_id: str, user: User = Depends(require_auth)):
    if order.owner_id != user.id:
        raise ForbiddenError()
```

### Password Hashing

```python
# ❌ NEVER: MD5, SHA1, SHA256 for passwords
hashed = hashlib.md5(password.encode()).hexdigest()

# ✅ Always: bcrypt, Argon2, or scrypt
hashed = bcrypt.hash(password, rounds=12)
```

---

## Never Log

- Passwords, PINs, security answers
- Full credit card numbers
- Authentication tokens, session IDs
- API keys, private keys
- Full SSNs, PHI, unmasked PII

## Do Log (Security Events)

- Authentication success/failure (with IP, timestamp)
- Authorization failures
- Input validation failures
- Admin/privileged actions
