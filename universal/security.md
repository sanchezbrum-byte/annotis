# Security Standards

> **Source:** OWASP Top 10:2021, OWASP ASVS 4.0, NIST Cybersecurity Framework, CWE/SANS Top 25 Most Dangerous Software Weaknesses

---

## 1. OWASP Top 10:2021

| Rank | Category | Description |
|------|----------|-------------|
| A01 | **Broken Access Control** | Failing to enforce restrictions on authenticated users. Most common vulnerability. |
| A02 | **Cryptographic Failures** | Weak encryption, cleartext transmission of secrets, weak algorithms (MD5, SHA1) |
| A03 | **Injection** | SQL, LDAP, OS command, XSS injection via untrusted data |
| A04 | **Insecure Design** | Missing threat modeling; fundamental design flaws that patches cannot fix |
| A05 | **Security Misconfiguration** | Default passwords, unnecessary features enabled, verbose error messages |
| A06 | **Vulnerable & Outdated Components** | Using components with known CVEs |
| A07 | **Identification & Authentication Failures** | Weak passwords, broken session management, missing MFA |
| A08 | **Software & Data Integrity Failures** | Auto-update without integrity checking; insecure CI/CD |
| A09 | **Security Logging & Monitoring Failures** | Insufficient logging; attackers operate undetected |
| A10 | **Server-Side Request Forgery (SSRF)** | Server fetching user-supplied URLs, bypassing internal firewalls |

---

## 2. Universal Security Rules

### 2.1 Secrets Management

```
NEVER hardcode:
  - API keys
  - Database passwords
  - Private keys / certificates
  - OAuth client secrets
  - Encryption keys
  - Internal service URLs with credentials
```

**Required:** Use environment variables (local) and a secret manager (production):
- AWS: AWS Secrets Manager or Parameter Store
- GCP: Secret Manager
- Azure: Key Vault
- Self-hosted: HashiCorp Vault

```bash
# ❌ BAD — secret in code
DATABASE_URL = "postgres://admin:super_secret@prod-db.internal/myapp"

# ✅ GOOD — from environment
import os
DATABASE_URL = os.environ["DATABASE_URL"]
```

If a secret is found in code:
1. **Rotate it immediately** — assume it is compromised
2. Remove it from code and git history (`git filter-repo`)
3. File a security incident report

### 2.2 Input Validation

**Validate at the boundary; trust inside the boundary.**

```python
# ✅ GOOD: Validate at the HTTP boundary before any processing
@router.post("/users")
def create_user(body: CreateUserRequest):  # Pydantic validates schema
    email = EmailAddress(body.email)       # Domain type validates business rules
    user = UserService.register(email, body.password)
    return user

# ❌ BAD: Validate deep inside business logic after data has been passed around
def save_user_to_db(conn, user_data: dict):
    if "@" not in user_data.get("email", ""):  # Too late; data already in system
        raise ValueError("Invalid email")
```

**Rules:**
- Validate **type, format, length, range, and business rules** at the boundary
- Reject-by-default: only accept known-good input, not block known-bad
- Do not rely on client-side validation alone — always re-validate on the server
- Sanitize for the **output context** (HTML-escape for HTML, parameterize for SQL)

### 2.3 Authentication & Authorization

- Authenticate first, then authorize. Never trust `user_id` from a request body — extract it from the validated session/token.
- Check authorization on every action, not just at login. A user who was admin yesterday may be deactivated today.
- Use established libraries for auth (Passport.js, Spring Security, Django Auth) — never roll your own JWT or session code
- Implement rate limiting on authentication endpoints to prevent brute-force

```python
# ❌ BAD: Trusting user-supplied ID
@router.get("/orders/{order_id}")
def get_order(order_id: str, user_id: str = Body(...)):  # User controls their ID
    return order_service.get(order_id)

# ✅ GOOD: User identity from validated token
@router.get("/orders/{order_id}")
def get_order(order_id: str, current_user: User = Depends(require_auth)):
    order = order_service.get(order_id)
    if order.owner_id != current_user.id:
        raise ForbiddenError()
    return order
```

### 2.4 Injection Prevention

**SQL Injection:**
```python
# ❌ BAD: String concatenation — SQLi vulnerability
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ GOOD: Parameterized queries
query = "SELECT * FROM users WHERE email = %s"
cursor.execute(query, (email,))
```

**Command Injection:**
```python
# ❌ BAD: shell=True with user input — RCE vulnerability
subprocess.run(f"ffmpeg -i {user_filename} output.mp4", shell=True)

# ✅ GOOD: List args, no shell interpolation
import shlex
safe_name = sanitize_filename(user_filename)
subprocess.run(["ffmpeg", "-i", safe_name, "output.mp4"])
```

**XSS Prevention:**
- Always escape output in the correct context (HTML, JS, CSS, URL)
- Use a Content Security Policy (CSP) header
- Use `HttpOnly` and `Secure` flags on session cookies

### 2.5 Cryptography

| Use Case | Use | Do NOT Use |
|----------|-----|-----------|
| Password hashing | bcrypt, Argon2, scrypt | MD5, SHA1, SHA256 (unsalted) |
| Data at rest | AES-256-GCM | DES, 3DES, RC4 |
| Data in transit | TLS 1.2+ | SSL, TLS 1.0, TLS 1.1 |
| Tokens/IDs | UUIDs v4 (random) or CSPRNG | Sequential integers |
| Signing | RSA-2048+, ECDSA P-256+ | RSA-1024 |
| Hashing for integrity | SHA-256, SHA-3 | MD5, SHA1 |

### 2.6 Logging Security

**Do NOT log:**
- Passwords, PINs, security questions/answers
- Full credit card numbers (last 4 digits are acceptable)
- Full SSNs (last 4 are acceptable)
- Authentication tokens, session IDs
- API keys
- Full personal health information (PHI)

**Do log:**
- Authentication attempts (success and failure) with timestamp and IP
- Authorization failures
- Input validation failures (helps detect attacks)
- Admin and privileged actions
- All security-relevant exceptions

**Log format:** Structured JSON with `timestamp`, `level`, `event_type`, `user_id`, `ip_address`, `request_id`.

---

## 3. Dependency Vulnerability Scanning

Run vulnerability scans as part of CI — block merges on critical/high CVEs:

| Language | Tool | Command |
|----------|------|---------|
| Python | `pip-audit` | `pip-audit --requirement requirements.txt` |
| JavaScript/Node | `npm audit` | `npm audit --audit-level=high` |
| Java | OWASP Dependency-Check | `./gradlew dependencyCheckAnalyze` |
| Go | `govulncheck` | `govulncheck ./...` |
| Rust | `cargo audit` | `cargo audit` |
| Ruby | `bundler-audit` | `bundle audit check --update` |

**Review dependencies quarterly:**
1. Remove unused dependencies
2. Upgrade outdated dependencies
3. Audit new dependencies before adding (check GitHub stars, maintenance status, CVE history)

---

## 4. Security Code Review Checklist

Before approving any PR, verify:

- [ ] No hardcoded secrets, passwords, or API keys
- [ ] All user inputs are validated and sanitized for their output context
- [ ] Authorization is checked before accessing any resource
- [ ] Database queries use parameterized statements (no string concatenation)
- [ ] Error messages do not expose stack traces or internal details to users
- [ ] Sensitive data is not logged
- [ ] New dependencies have been vetted (no known CVEs)
- [ ] File operations use safe path handling (no path traversal risk)
- [ ] External URLs fetched by the server are from an allowlist (SSRF prevention)

---

## 5. Threat Modeling

For new features that handle sensitive data, perform a threat model before implementation:

1. **What data does this feature handle?** (PII, financial, health, credentials)
2. **Who are the threat actors?** (External attacker, malicious insider, compromised dependency)
3. **What are the attack surfaces?** (HTTP endpoints, file uploads, admin console)
4. **STRIDE analysis:**
   - **S**poofing: Can an attacker impersonate a legitimate user or service?
   - **T**ampering: Can data be modified in transit or at rest?
   - **R**epudiation: Can actions be denied without an audit trail?
   - **I**nformation Disclosure: Can sensitive data be leaked?
   - **D**enial of Service: Can the service be made unavailable?
   - **E**levation of Privilege: Can a user escalate to admin rights?
