# Architecture Standards

> **Source:** "Clean Architecture" (Robert C. Martin), "Implementing Domain-Driven Design" (Vernon), "Designing Data-Intensive Applications" (Kleppmann), Hexagonal Architecture (Alistair Cockburn, 2005)

---

## 1. Clean Architecture

Clean Architecture organizes code into concentric layers, where dependencies point **inward only**. The inner layers know nothing about the outer layers.

```
┌─────────────────────────────────────────────────────────┐
│ Frameworks & Drivers                                      │
│   (Web, DB, UI, External APIs)                           │
│  ┌───────────────────────────────────────────────────┐   │
│  │ Interface Adapters                                 │   │
│  │   (Controllers, Gateways, Presenters)              │   │
│  │  ┌─────────────────────────────────────────────┐  │   │
│  │  │ Application Business Rules                   │  │   │
│  │  │   (Use Cases / Application Services)         │  │   │
│  │  │  ┌───────────────────────────────────────┐  │  │   │
│  │  │  │ Enterprise Business Rules              │  │  │   │
│  │  │  │   (Entities / Domain Objects)          │  │  │   │
│  │  │  └───────────────────────────────────────┘  │  │   │
│  │  └─────────────────────────────────────────────┘  │   │
│  └───────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### The Dependency Rule

> Source code dependencies must point only **inward** — toward higher-level policies.

- Entities know nothing about Use Cases
- Use Cases know nothing about Controllers or Databases
- Controllers know nothing about the Database implementation
- The Database can be swapped for a different implementation without changing business rules

### Layer Responsibilities

| Layer | Contains | Must NOT contain |
|-------|----------|-----------------|
| **Entities** | Domain objects, business rules, value objects | Framework imports, DB queries, HTTP logic |
| **Use Cases** | Application-specific business rules, orchestration | Framework imports, DB drivers, UI logic |
| **Interface Adapters** | Controllers, presenters, gateways, mappers | Business rules, DB schema details |
| **Frameworks** | Spring/Express/Django, ORM, HTTP clients | Business rules, domain logic |

### Common Violations

❌ Database call in a domain entity:
```python
class Order:
    def submit(self):
        db.execute("INSERT INTO orders ...")  # Domain entity knows about DB
```

❌ Business rule in a controller:
```python
@app.post("/orders")
def create_order(data):
    if data.total > user.credit_limit * 0.8:  # Business rule in controller
        return 400, "Exceeds credit limit"
```

✅ Correct:
```python
# Domain entity — pure business rule
class Order:
    def submit(self, user: User) -> None:
        if self.total > user.available_credit:
            raise InsufficientCreditError(required=self.total)

# Use case — orchestration
class SubmitOrderUseCase:
    def execute(self, order_id: str, user_id: str) -> OrderConfirmation:
        order = self._order_repo.find(order_id)
        user = self._user_repo.find(user_id)
        order.submit(user)
        self._order_repo.save(order)
        self._event_bus.publish(OrderSubmittedEvent(order))
        return OrderConfirmation.from_order(order)

# Controller — HTTP adapter
@router.post("/orders/{order_id}/submit")
def submit_order(order_id: str, user_id: str = Depends(get_current_user)):
    return submit_order_use_case.execute(order_id, user_id)
```

---

## 2. Hexagonal Architecture (Ports & Adapters)

Hexagonal Architecture (Cockburn, 2005) is an alternative framing of Clean Architecture that emphasizes **symmetry** between driving (left) and driven (right) actors.

```
         Driving Actors                    Driven Actors
     (HTTP, CLI, Tests)              (DB, Email, Queue, APIs)
           │                                   │
           ▼                                   ▼
    ┌──────────────┐                  ┌────────────────┐
    │  Input Port  │                  │  Output Port   │
    │  (interface) │                  │  (interface)   │
    └──────┬───────┘                  └────────┬───────┘
           │          ┌──────────┐            │
           └─────────►│  Domain  │◄───────────┘
                      │  (Core)  │
                      └──────────┘
```

- **Ports**: Interfaces (abstractions) defined in the domain core
- **Adapters**: Concrete implementations outside the core that implement those interfaces

**When to use Hexagonal over Clean Architecture:**
- When you need to support multiple delivery mechanisms (HTTP + CLI + gRPC) symmetrically
- When testability is the primary concern — the hexagon can be tested without any infrastructure
- For microservices where the boundary is explicit

---

## 3. Folder Structure Conventions

### Feature-Based (Recommended for Large Applications)

```
src/
  features/
    orders/
      domain/
        order.py
        order_repository.py   # Port (interface)
      application/
        submit_order.py       # Use case
        cancel_order.py
      adapters/
        http/
          orders_controller.py
        persistence/
          postgres_order_repo.py  # Adapter (implements port)
    payments/
      domain/...
      application/...
      adapters/...
  shared/
    domain/
      value_objects.py
      base_entity.py
    infrastructure/
      database.py
      event_bus.py
```

### Layer-Based (Simple Applications)

```
src/
  domain/
  application/
  adapters/
    http/
    persistence/
    messaging/
  shared/
```

**Rule:** Prefer feature-based as the application grows. Start with layer-based; refactor to feature-based when any layer folder exceeds ~20 files.

---

## 4. Design Patterns — When to Use and When NOT To

### Use These Patterns When the Problem Genuinely Matches

| Pattern | Use When | Do NOT Use When |
|---------|----------|-----------------|
| **Strategy** | Multiple interchangeable algorithms | Only one algorithm exists (YAGNI) |
| **Factory** | Object creation is complex or needs abstraction | `new Foo()` is simple enough |
| **Repository** | Need to abstract data persistence layer | No need to swap DB; adds indirection for nothing |
| **Observer/Event** | Multiple consumers of the same event | Two components need direct communication |
| **Decorator** | Add behavior to objects without modifying them | Only one layer of behavior needed |
| **Command** | Undo/redo, queuing, audit log | Simple function call is sufficient |
| **Facade** | Simplify a complex subsystem interface | Subsystem is already simple |

### Anti-Patterns to Avoid

| Anti-Pattern | Description | Fix |
|-------------|-------------|-----|
| **God Object** | One class knows and does everything | Apply SRP; split into focused objects |
| **Anemic Domain Model** | Domain objects are data bags; all logic in services | Move business rules into entities |
| **Service Locator** | Dependencies looked up from global registry | Use constructor injection |
| **Singleton abuse** | Everything is a singleton for "convenience" | Use DI container to manage lifetime |
| **Shotgun Surgery** | One change requires modifications in many places | Encapsulate the concern |
| **Feature Envy** | A method uses another class's data excessively | Move the method to the class it envies |
| **Primitive Obsession** | Using primitives for domain concepts (`string` for `Email`) | Introduce value objects |

---

## 5. When to Create Abstractions

The **Rule of Three** (Martin Fowler): Abstract on the third occurrence, not the second.

- **1st time**: Just do it directly
- **2nd time**: Note the duplication; resist abstracting
- **3rd time**: Refactor to a shared abstraction

**Checklist before creating an interface/abstract class:**
- [ ] Are there currently two or more concrete implementations?
- [ ] Is there a test-only reason to abstract (for mocking)? (This is valid)
- [ ] Does the abstraction have a clear, named concept? (not just `IFoo` wrapping `Foo`)
- [ ] Will callers depend on the abstraction, not the concrete implementation?

If you cannot answer yes to at least two of these: don't abstract yet.

---

## 6. Dependency Direction Rules

1. Domain entities → nothing (no external dependencies)
2. Use cases → domain entities, port interfaces
3. Adapters → use cases (implement ports)
4. Frameworks → adapters

**Test:** Can you unit-test your domain and use case layers without starting a server, connecting to a database, or making a network call? If not, you have violated the dependency direction rule.

---

## 7. Microservices vs Monolith

**Start with a monolith.** Extract services only when you have a clear reason.

### Valid Reasons to Extract a Service
- Different scaling requirements (payments needs 100x traffic; profile editing does not)
- Different deployment cadences (ML model updates vs stable CRUD)
- Different technology requirements (real-time video processing needs Rust; admin panel is fine in Django)
- Team autonomy (two teams of 6+ engineers own the same area)
- Regulatory isolation (PCI scope reduction)

### Invalid Reasons
- "It feels like it should be separate"
- "Microservices are modern"
- "We'll scale later" (YAGNI — scale when you actually need to)
- Team size is < 20 engineers (2-pizza-rule teams rarely need microservices)

### The Distributed Monolith Warning

If your services always deploy together, share a database, or fail together — you have a distributed monolith. This is the worst of both worlds. Fix it or merge back into a monolith.
