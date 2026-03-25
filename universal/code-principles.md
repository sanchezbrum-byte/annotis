# Code Principles

> **Source:** "Clean Code" and "Clean Architecture" (Robert C. Martin), "Design Patterns" (Gang of Four), "A Philosophy of Software Design" (John Ousterhout), "The Pragmatic Programmer" (Hunt & Thomas)

---

## 1. SOLID Principles

### S — Single Responsibility Principle

> "A class should have one, and only one, reason to change."

Every module, class, or function should have **one job** and **one owner** (the actor or stakeholder who would request changes to it).

❌ **Violation:**
```python
class UserService:
    def register_user(self, email: str, password: str) -> User:
        # Authentication concern
        hashed = bcrypt.hash(password)
        # Persistence concern
        user = self.db.insert("users", email=email, password=hashed)
        # Email concern
        self.smtp.send(email, "Welcome!", "Thanks for signing up!")
        # Metrics concern
        self.metrics.increment("user.registered")
        return user
```

✅ **Fix:**
```python
class UserRegistrationService:
    def __init__(self, auth: AuthService, repo: UserRepository,
                 notifier: NotificationService, metrics: MetricsClient):
        self._auth = auth
        self._repo = repo
        self._notifier = notifier
        self._metrics = metrics

    def register(self, email: str, password: str) -> User:
        hashed = self._auth.hash_password(password)
        user = self._repo.save(User(email=email, password=hashed))
        self._notifier.send_welcome(user)
        self._metrics.increment("user.registered")
        return user
```

---

### O — Open/Closed Principle

> "Software entities should be open for extension, but closed for modification."

Add new behavior by adding new code — not by modifying existing, tested code.

❌ **Violation:**
```python
def calculate_area(shape):
    if shape.type == "circle":
        return math.pi * shape.radius ** 2
    elif shape.type == "rectangle":
        return shape.width * shape.height
    # Adding a new shape requires modifying this function ← violation
```

✅ **Fix:**
```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

class Circle(Shape):
    def area(self) -> float:
        return math.pi * self.radius ** 2

class Rectangle(Shape):
    def area(self) -> float:
        return self.width * self.height

# Adding Triangle: create a new class, no existing code changes
class Triangle(Shape):
    def area(self) -> float:
        return 0.5 * self.base * self.height
```

---

### L — Liskov Substitution Principle

> "Objects of a subclass should be substitutable for objects of the superclass without altering the correctness of the program."

A subclass must honor the **contract** of its parent — same preconditions, same postconditions, same invariants.

❌ **Violation:**
```python
class Rectangle:
    def set_width(self, w): self._width = w
    def set_height(self, h): self._height = h
    def area(self): return self._width * self._height

class Square(Rectangle):
    def set_width(self, w):   # Breaks Rectangle's contract
        self._width = w
        self._height = w      # Side-effect violates caller expectations
```

✅ **Fix:** If Square cannot honor Rectangle's contract, they should not share an inheritance relationship. Use composition or a separate `Shape` interface.

---

### I — Interface Segregation Principle

> "Clients should not be forced to depend on interfaces they do not use."

Prefer many small, focused interfaces over one large general-purpose one.

❌ **Violation:**
```typescript
interface Worker {
  work(): void;
  eat(): void;   // Robot workers cannot eat — forced to implement meaninglessly
  sleep(): void; // Robot workers cannot sleep
}
```

✅ **Fix:**
```typescript
interface Workable { work(): void; }
interface Feedable { eat(): void; }
interface Restable { sleep(): void; }

class HumanWorker implements Workable, Feedable, Restable { ... }
class RobotWorker implements Workable { ... }
```

---

### D — Dependency Inversion Principle

> "High-level modules should not depend on low-level modules. Both should depend on abstractions."

Business logic should not import database drivers, HTTP clients, or file system libraries directly.

❌ **Violation:**
```python
from myapp.infrastructure.postgres import PostgresUserRepository

class OrderService:
    def __init__(self):
        self._users = PostgresUserRepository()  # Hardcoded infrastructure dependency
```

✅ **Fix:**
```python
from myapp.domain.ports import UserRepository  # Abstract interface

class OrderService:
    def __init__(self, users: UserRepository):  # Injected abstraction
        self._users = users
```

---

## 2. DRY — Don't Repeat Yourself

> "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."

**The nuance:** The wrong abstraction is worse than duplication. Do not DRY up code that appears similar but represents different concepts.

❌ **Wrong DRY (coincidental duplication):**
```python
# These two functions look the same but represent different business concepts.
# Combining them creates coupling between unrelated domains.
def validate_user_email(email: str) -> bool:
    return "@" in email and "." in email

def validate_order_email(email: str) -> bool:  # Different business rule
    return "@" in email and "." in email

# Don't merge these into one — they will diverge as requirements change.
```

✅ **Correct DRY (true duplication):**
```python
# The same JWT validation logic copied in 6 different controllers.
# This is true duplication — one fact (JWT is valid) expressed many times.
def validate_jwt(token: str, secret: str) -> Claims:
    """Extract and validate JWT claims. Single source of truth for JWT logic."""
    ...
```

**Rule:** Before abstracting, ask: "Would both usages always change together?" If yes: DRY. If no: leave them separate.

---

## 3. KISS — Keep It Simple, Stupid

> "Simplicity is the ultimate sophistication." — da Vinci (attributed)

Write the simplest code that correctly solves the problem. Complexity is a cost — justify every abstraction you add.

❌ **Overcomplicated:**
```python
class AbstractFactoryStrategyDecoratorObserverBuilder:
    def build_with_strategy(self, strategy_factory_fn):
        return strategy_factory_fn()(self._build_base())
```

✅ **Simple:**
```python
def send_welcome_email(user: User) -> None:
    """Send a welcome email to a newly registered user."""
    subject = f"Welcome, {user.first_name}!"
    body = render_template("welcome.html", user=user)
    email_client.send(to=user.email, subject=subject, body=body)
```

---

## 4. YAGNI — You Aren't Gonna Need It

> "Always implement things when you actually need them, never when you just foresee that you need them."

Common violations to avoid:

| YAGNI Violation | What Was Actually Needed |
|----------------|--------------------------|
| Generic plugin system for one use case | One hardcoded implementation |
| Abstract `IUserRepository` when there's only Postgres | Concrete `PostgresUserRepository` |
| Multi-tenant data model for a single-tenant MVP | Simple single-tenant schema |
| Event sourcing for a simple CRUD app | Regular database update |
| Microservices for a 2-person team | Monolith |
| Caching layer before profiling | Direct database call |

**Rule:** Implement the feature as if there is no future. When the future arrives with new requirements, refactor then. Upfront abstraction based on guesses is the leading cause of over-engineered codebases.

---

## 5. Law of Demeter (Principle of Least Knowledge)

> "Talk only to your immediate friends."

A method should call methods on: its own object, its parameters, objects it creates, and its direct fields — never on objects returned from those calls.

❌ **Violation ("Train Wreck"):**
```python
# This line is fragile: any change to Order, Payment, or Card breaks OrderService
charge_amount = order.get_payment().get_card().get_credit_limit()
```

✅ **Fix:**
```python
# Order knows its payment capacity; OrderService does not need to know the chain
charge_amount = order.get_available_credit()
```

**Structural test:** Count the dots. More than two consecutive method calls on different objects is a warning sign.

---

## 6. Principle of Least Surprise

Code should behave consistently with what readers expect, based on its name and context.

- A function named `getUser()` should never modify state
- A function named `isValid()` should return a boolean, not throw an exception
- A `User.save()` method should save the user — not send an email as a side effect

---

## 7. Fail Fast

Validate inputs and invariants **as early as possible**. Never let invalid state propagate deep into the system where the error is confusing and the fix is unclear.

```python
def process_payment(amount: Decimal, currency: str) -> PaymentResult:
    if amount <= 0:
        raise ValueError(f"Payment amount must be positive, got: {amount}")
    if currency not in SUPPORTED_CURRENCIES:
        raise ValueError(f"Unsupported currency: {currency}")
    # Now process safely, knowing inputs are valid
    ...
```

---

## 8. Composition Over Inheritance

Prefer composing behavior from small, single-purpose objects over deep inheritance hierarchies.

**Inheritance is appropriate when:**
- There is a genuine IS-A relationship
- The parent class's contract is fully honored by the child (LSP)
- The hierarchy is shallow (≤ 2–3 levels)

**Use composition when:**
- You want to reuse behavior without the IS-A relationship
- You need to combine multiple behaviors
- The hierarchy would be deeper than 3 levels
