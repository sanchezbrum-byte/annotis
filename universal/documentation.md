# Documentation Standards

> **Source:** "Docs for Developers" (Bhatti et al.), Google Developer Documentation Style Guide, Divio Documentation System, Architecture Decision Records (Michael Nygard)

---

## 1. Documentation Types

| Type | Purpose | Audience | Format |
|------|---------|---------|--------|
| **API Reference** | What every function/method does | Developers integrating | Docstrings + generated docs |
| **README** | What the project is; how to run it | New team members | Markdown |
| **Architecture Decision Record (ADR)** | Why a decision was made | Future maintainers | Markdown (docs/adr/) |
| **Runbook** | How to operate the system | On-call engineers | Markdown |
| **CHANGELOG** | What changed between versions | Users/consumers | Markdown (Conventional format) |
| **Tutorial** | Step-by-step learning | Newcomers | Markdown with examples |

---

## 2. README Requirements

Every repository root MUST have a README.md containing:

```markdown
# Project Name

One-sentence description of what this project does.

## Overview

2–3 paragraphs: what problem it solves, who uses it, key concepts.

## Prerequisites

- Node.js >= 20.x
- Docker >= 24.x
- PostgreSQL >= 16

## Getting Started

# Clone and run in < 5 minutes:
git clone git@github.com:org/repo.git
cd repo
cp .env.example .env
docker compose up -d
npm install
npm run dev

## Architecture

High-level diagram or link to architecture.md

## Contributing

Link to CONTRIBUTING.md

## License
```

**Rules:**
- Must be runnable by a new team member with zero tribal knowledge
- "Getting started" section must work — test it on a fresh machine at least quarterly
- Keep it updated — an outdated README is worse than no README

---

## 3. Docstring Standards

Write docstrings for:
- All public functions and methods
- All public classes
- All modules (file-level docstrings)

Do NOT write docstrings for:
- Private internal helpers with obvious names (`_build_cache()`)
- Trivial getters/setters
- Test functions (use descriptive test names instead)

### Required Docstring Fields

For public, non-trivial functions:

| Field | Required When |
|-------|--------------|
| Summary | Always (one line) |
| Description | When behavior is non-obvious |
| Args/Parameters | When function has parameters |
| Returns | When return value is non-obvious |
| Raises | When exceptions can be raised |
| Example | For utility functions, public APIs |

See language-specific guides for exact format (Google style, JSDoc, Javadoc, etc.).

---

## 4. Inline Comment Rules

**Comment the WHY, not the WHAT.** The code shows what; comments explain why.

```python
# ❌ BAD: narrates what the code does (noise)
# Increment counter by 1
count += 1

# ❌ BAD: obvious
# Return the user
return user

# ✅ GOOD: explains non-obvious reasoning
# Stripe requires idempotency keys to prevent double-charges on network retries.
# Key expires after 24h, matching Stripe's deduplication window.
idempotency_key = f"{order_id}:{int(time.time() // 86400)}"

# ✅ GOOD: warns about a gotcha
# NOTE: Do not use cache.get() here — it triggers a Redis pipeline flush
# which causes a 200ms stall under high load. Use cache.get_raw() instead.
value = cache.get_raw(key)
```

---

## 5. TODO/FIXME Format

Every TODO or FIXME must include: author, date, and a ticket reference.

```python
# TODO(alice@example.com, 2025-03-15, INFRA-423): Replace with async client
# when python-kafka 3.x releases stable async support.
result = kafka_client.produce_sync(topic, message)

# FIXME(bob@example.com, 2025-02-01, PAY-887): This calculation overflows
# for orders > $999,999. Short-term workaround until we migrate to Decimal.
total = int(amount_cents) * quantity
```

**Rule:** No TODO without a ticket. No ticket-less TODOs should pass code review.

---

## 6. Dead Code

**Never comment out code. Delete it.**

Commented-out code is:
- Confusing (why is it there? is it coming back? is it safe to delete?)
- Decaying (it rots as the codebase changes around it)
- Unnecessary (git history preserves all previous versions)

```python
# ❌ BAD: commented-out dead code
# def old_payment_handler(amount):
#     # This was the old Stripe v2 handler
#     charge = stripe.Charge.create(amount=amount)
#     return charge.id

# ✅ GOOD: just delete it; git history has the old version
```

---

## 7. Architecture Decision Records (ADRs)

Record significant architectural decisions in `docs/adr/` using this format:

```markdown
# ADR-0023: Use PostgreSQL for primary data storage

**Date:** 2025-03-15
**Status:** Accepted
**Deciders:** Alice (CTO), Bob (Staff Eng), Carol (Backend Lead)

## Context

We need a primary relational data store. The options considered were:
PostgreSQL, MySQL, CockroachDB, and Amazon Aurora.

## Decision

We will use PostgreSQL 16 running on Amazon RDS.

## Rationale

- PostgreSQL has richer feature set (JSONB, window functions, full-text search)
- Team has deep PostgreSQL expertise; zero MySQL/CockroachDB experience
- RDS managed service reduces operational burden
- Cost at our current scale: ~$200/month vs $800/month for Aurora

## Consequences

- Positive: Rich query capabilities; familiar tooling; managed backups/failover
- Negative: Manual horizontal sharding if we exceed single-node write limits
- Mitigation: Monitor write throughput; evaluate read replicas at 50k RPS

## Alternatives Rejected

- MySQL: Less feature-rich; no JSONB; team preference strongly PostgreSQL
- CockroachDB: No team expertise; licensing changes in 2024 a concern
- Aurora: 4x cost; premature optimization at current scale
```

**When to write an ADR:**
- Choosing a database, message broker, or framework
- Defining a service boundary
- Changing an API contract
- Adopting or deprecating a pattern

**ADR Numbering:** Sequential integers, zero-padded to 4 digits: `ADR-0001`.

---

## 8. CHANGELOG Format

Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) with Conventional Commits:

```markdown
# Changelog

All notable changes to this project will be documented in this file.
Format: [Semantic Versioning](https://semver.org/)

## [Unreleased]

### Added
- New `POST /orders/{id}/refund` endpoint for partial refunds (#1523)

### Fixed
- Race condition in order confirmation emails (#1489)

## [2.4.0] — 2025-03-01

### Added
- OAuth2 PKCE flow for mobile clients (#1421)
- Rate limiting on authentication endpoints: 5 req/min per IP (#1398)

### Changed
- Minimum TLS version raised from 1.1 to 1.2 (#1402)

### Deprecated
- `GET /api/v1/users` — use `GET /api/v2/users` instead (removes 2025-09-01)

### Removed
- Legacy XML response format (deprecated in v2.0.0) (#1399)

### Security
- Patched XSS vulnerability in markdown renderer (CVE-2025-1234) (#1501)
```
