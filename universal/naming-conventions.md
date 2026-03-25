# Naming Conventions

> **Source:** "Clean Code" (Robert C. Martin), Google Style Guides (multiple languages), "The Art of Readable Code" (Boswell & Foucher)

---

## 1. Universal Naming Rules

These rules apply across all languages:

1. **Names must be self-explanatory** — a name should tell you what it is and why it exists without needing a comment
2. **Avoid abbreviations** unless they are universally understood (`id`, `url`, `api`, `http`)
3. **Be consistent** — if you call it `user_id` in one place, use `user_id` everywhere
4. **Length should match scope** — short names (`i`, `n`) are fine in a 3-line loop, terrible in a 30-line function
5. **Avoid encodings** — no Hungarian notation (`strName`), no type prefixes (`intCount`)
6. **Avoid noise words** — `UserData`, `UserInfo`, `UserObject` all mean the same thing; pick one

---

## 2. Cross-Language Convention Table

| Concept | Python | JavaScript/TypeScript | Java | Go | Rust | C++ (Google) |
|---------|--------|----------------------|------|-----|------|------|
| Variable | `snake_case` | `camelCase` | `camelCase` | `camelCase` | `snake_case` | `snake_case` |
| Constant | `UPPER_SNAKE_CASE` | `UPPER_SNAKE_CASE` | `UPPER_SNAKE_CASE` | `ALL_CAPS` | `SCREAMING_SNAKE_CASE` | `kCamelCase` |
| Function | `snake_case` | `camelCase` | `camelCase` | `camelCase` | `snake_case` | `CamelCase` |
| Class | `PascalCase` | `PascalCase` | `PascalCase` | `PascalCase` | `PascalCase` | `PascalCase` |
| Interface | N/A (Protocol) | `IPascalCase` or `PascalCase` | `PascalCase` | `PascalCase` | (traits) | N/A |
| File | `snake_case.py` | `camelCase.ts` or `kebab-case.ts` | `PascalCase.java` | `snake_case.go` | `snake_case.rs` | `snake_case.cc` |
| Package | `lowercase` | `kebab-case` (npm) | `com.company.app` | `lowercase` | `snake_case` | N/A |

---

## 3. Boolean Naming Patterns

Boolean variables and functions must read as yes/no questions:

```python
# ✅ GOOD — reads as a question
is_active = True
has_permission = False
should_retry = True
can_delete = False
was_modified = True
will_expire = False

# ❌ BAD — ambiguous
active = True        # is this an object or a flag?
permission = False   # what about permission?
flag = True          # meaningless
status = True        # what status?
check = False        # check what?
```

**Prefixes:**
- `is_` — current state: `is_authenticated`, `is_empty`, `is_valid`
- `has_` — possession: `has_children`, `has_subscription`, `has_error`
- `should_` — recommendation or pending action: `should_refresh`, `should_retry`
- `can_` — capability: `can_edit`, `can_delete`, `can_publish`
- `was_` — past state: `was_deleted`, `was_processed`
- `will_` — future state: `will_expire`, `will_notify`

---

## 4. Function/Method Naming Patterns

### Commands (mutate state) — use verbs
```
create_user, delete_order, send_email, process_payment,
update_profile, publish_event, reset_password
```

### Queries (return data without side effects) — use nouns or `get_`/`find_`
```
get_user, find_orders_by_status, calculate_total,
load_config, fetch_remote_data, count_active_sessions
```

### Predicate functions (return boolean) — use `is_`/`has_`/`can_`
```
is_valid, has_access, can_proceed, should_retry
```

### Event handlers — use `on_` prefix
```
on_click, on_message_received, on_payment_completed, on_error
```

---

## 5. Test Function Naming

**Pattern:** `<method>_<scenario>_<expected_behavior>`

```python
# Python
def test_calculate_total_with_empty_cart_returns_zero():
def test_calculate_total_with_discount_applies_percentage():
def test_charge_card_when_expired_raises_payment_error():
def test_find_user_when_not_found_returns_none():
```

```java
// Java (JUnit 5)
@Test void calculateTotal_withEmptyCart_returnsZero()
@Test void chargeCard_whenExpired_throwsPaymentException()
@Test void findUser_whenNotFound_returnsEmpty()
```

```javascript
// JavaScript (Jest/Mocha)
describe('calculateTotal', () => {
    it('returns zero for an empty cart')
    it('applies percentage discount correctly')
})
describe('chargeCard', () => {
    it('throws PaymentError when card is expired')
})
```

---

## 6. What to Avoid

| Anti-Pattern | Example | Fix |
|-------------|---------|-----|
| Single-letter names outside loops | `d`, `x`, `t` | `discount`, `position`, `timestamp` |
| Numeric suffixes | `user1`, `user2`, `temp2` | Descriptive: `primary_user`, `secondary_user` |
| Generic names | `data`, `info`, `value`, `result`, `obj`, `stuff` | Describe what the data is |
| Misleading names | `list` for a `dict` | Match the name to the actual type/concept |
| Negated booleans | `is_not_active`, `no_errors` | `is_inactive`, `has_errors` |
| Type in name | `user_list`, `name_string`, `count_int` | `users`, `name`, `count` |
| Acronyms unless universal | `cstmrTxn` | `customer_transaction` |
| Context repetition | `user.user_name`, `order.order_total` | `user.name`, `order.total` |

---

## 7. Domain Vocabulary

Use the language of the business domain — not generic technical terms:

```python
# ❌ BAD: technical terms that obscure business meaning
def process_data(input_list):
    return [transform_item(x) for x in input_list if filter_check(x)]

# ✅ GOOD: domain language
def calculate_eligible_refunds(transactions: list[Transaction]) -> list[Refund]:
    return [Refund.from_transaction(t) for t in transactions if t.is_refundable()]
```

Establish a **ubiquitous language** (Domain-Driven Design term) with the business team. When the business says "order", the code says `Order` — not `Transaction`, `Purchase`, or `Request`. Alignment between code vocabulary and business vocabulary is a major force multiplier for maintainability.
