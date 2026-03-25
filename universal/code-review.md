# Code Review Standards

> **Source:** Google Engineering Practices (eng-practices), "How to Do Code Reviews Like a Human" (Michael Lynch), "The Art of Readable Code" (Boswell & Foucher)

---

## 1. Core Principle

The purpose of code review is to **maintain code health** and **share knowledge** — not to catch every possible issue or enforce personal preferences. A reviewer's job is to ensure the codebase is incrementally better after each change, not perfect.

> "The author of a CL should not need to justify every style choice if it is reasonable and matches the existing codebase." — Google Engineering Practices

---

## 2. What Reviewers MUST Check

These items are blocking — a PR should not merge without addressing them:

### ✅ Correctness
- Does the code do what the description says it does?
- Are there edge cases that would cause incorrect behavior? (null, empty, boundary values)
- Is concurrency handled correctly? (race conditions, deadlocks, shared mutable state)
- Does the code handle errors explicitly? Are errors propagated correctly?

### ✅ Tests
- Are new tests included for new behavior?
- Do the tests actually test what the author claims they test?
- Are critical paths tested? (the code that handles money, auth, data integrity)
- Do tests follow the AAA pattern and naming convention?

### ✅ Security
- Are inputs validated at the boundary?
- Could this code enable SQL injection, XSS, SSRF, or path traversal?
- Are credentials, secrets, or PII being logged or returned in API responses?
- Is authorization checked before data access? (not just authentication)

### ✅ Performance
- Is there an obvious O(n²) or worse algorithm where O(n log n) would work?
- Is there a database query inside a loop? (N+1 query problem)
- Is there a missing index for a query on a large table?
- Are large objects being copied unnecessarily?

### ✅ Readability & Naming
- Can you understand what the code does in < 60 seconds without documentation?
- Are variable, function, and class names clear and consistent with the codebase?
- Is the complexity appropriate for the problem being solved?
- Is there dead code, commented-out code, or debug logging?

### ✅ API Design (for public interfaces)
- Is the API consistent with existing patterns in the codebase?
- Is it possible to misuse this API in a way that causes silent failures?
- Will this API still make sense in 6 months when the context is forgotten?

---

## 3. What Reviewers Should NOT Block On

Do not hold up a merge for:

- Personal style preferences that are **not covered by the team's linter** — if the linter allows it, it's allowed
- Architectural preferences when the author's approach is **also reasonable**
- Minor naming disagreements when the name is **clear and consistent**
- Adding features that are **out of scope** for this PR (open a ticket instead)
- Demanding rewrites to perfectly match how you would have written it

If you find yourself writing "I would have done this differently...", ask yourself: is the author's approach wrong or just different? If it's just different, use `[nit]` or leave it out.

---

## 4. Review Tone and Language

Adapted from Google's Engineering Practices documentation on respectful reviews:

### ✅ DO
- Ask questions instead of making demands: "What happens if `user` is null here?" instead of "This crashes on null"
- Explain the why: "This could cause a race condition when two requests arrive simultaneously because..."
- Offer alternatives: "An alternative would be to use a database transaction here — would that work?"
- Acknowledge good work: "Nice use of the strategy pattern here — very clean."
- Prefix feedback type: `[blocking]`, `[nit]`, `[question]`, `[suggestion]`

### ❌ DON'T
- Use "you" language that attacks the person: "You wrote this wrong"
- Be sarcastic or condescending: "Obviously this doesn't handle nulls"
- Leave vague, actionless comments: "This is messy" — be specific about what and why
- Require a video call to explain a written comment — comments should be self-explanatory
- Approve with blocking issues still open

### Comment Prefixes (Required)

```
[blocking] This will cause a NPE when the user has no active subscription.
[nit] Consider renaming `d` to `discount` for clarity.
[question] Why do we need to call flush() here? Is autocommit disabled?
[suggestion] We could use a bulk insert here instead of a loop — might be worth it at scale.
[praise] Elegant solution to the retry logic — much cleaner than what we had.
```

---

## 5. Time Expectations

| Role | Expectation |
|------|-------------|
| **Reviewer** | First response within **1 business day** of review request |
| **Reviewer** | Approval or blocking feedback within **2 business days** |
| **Author** | Respond to all comments within **1 business day** |
| **Author** | Re-request review after addressing all blocking comments |
| **Tech Lead** | Resolve stalemates within **1 business day** of being tagged |

If a PR sits unreviewed for > 2 business days, the author should ping in the team channel — not as a complaint, as a reminder.

---

## 6. PR Author Pre-Submission Checklist

Complete before clicking "Request Review":

```
Self-review checklist:
- [ ] I have read my own diff as if I were a reviewer (line by line)
- [ ] All CI checks pass (tests, lint, security scan, coverage)
- [ ] No debug logs, print statements, or TODO without ticket reference
- [ ] No hardcoded secrets, credentials, or API keys
- [ ] PR description is filled in: What, How, Testing, Related tickets
- [ ] PR size is ≤ 400 lines changed (if larger, split it)
- [ ] New code has tests; critical paths have 100% coverage
- [ ] Dependent PRs are listed and ordered
- [ ] CHANGELOG.md updated for user-visible changes
- [ ] Any breaking changes are clearly documented
```

---

## 7. Reviewer Checklist

```
Reviewer checklist:
- [ ] I understand what this PR is trying to do (re-read the description)
- [ ] I've checked for correctness in the core logic path
- [ ] I've checked all error handling paths
- [ ] I've reviewed the tests — do they actually test behavior?
- [ ] I've checked for security issues (injections, auth bypass, data exposure)
- [ ] I've flagged any performance concerns with evidence, not intuition
- [ ] All my comments have clear explanations of the why
- [ ] I've distinguished blocking from non-blocking comments
- [ ] I've approved or requested changes — no "LGTM" without reading
```

---

## 8. Handling Disagreements

1. **Both parties** should default to the principle: "What is best for the long-term health of the codebase?"
2. **The reviewer** should not insist on their preference unless there is a concrete harm
3. **The author** should not dismiss feedback without engaging with the reasoning
4. If genuinely stuck: escalate to the **tech lead** — do not let a PR sit blocked for more than 2 days
5. If it is a significant architectural disagreement: schedule a 30-minute discussion; do not litigate architecture in PR comments
6. **Document the decision**: add a comment explaining the chosen approach and why, so future readers have context

### When Author Can Override Reviewer

The author can merge without full consensus if:
- The reviewer's only objection is a `[nit]` or style preference
- Two other team members have approved
- The reviewer has not responded within 2 business days after being pinged twice

### When Reviewer Can Escalate

A reviewer can escalate to the tech lead if:
- A security or data integrity issue is being dismissed
- A pattern is being introduced that conflicts with team conventions
- The author is unresponsive

---

## 9. Large PR Splitting Strategy

When a feature is too large for one PR:

```
PR 1: [refactor] extract PaymentProcessor interface (no behavior change)
PR 2: [feat] implement StripePaymentProcessor behind feature flag
PR 3: [feat] add PayPal as fallback processor
PR 4: [chore] enable feature flag in production, remove old code
```

Each PR must:
- Be independently mergeable (does not break main)
- Have a clear purpose stated in its title
- Be reviewable in < 2 hours
