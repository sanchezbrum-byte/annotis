# Go Concurrency

---

## Goroutine Ownership (Google Go Style)

**Rule:** Every goroutine must have a clear owner responsible for stopping it.

```go
// ✅ GOOD: goroutine with explicit lifecycle
type Worker struct {
    cancel context.CancelFunc
    done   chan struct{}
}

func NewWorker(ctx context.Context, jobs <-chan Job) *Worker {
    ctx, cancel := context.WithCancel(ctx)
    w := &Worker{cancel: cancel, done: make(chan struct{})}
    go w.run(ctx, jobs)
    return w
}

func (w *Worker) run(ctx context.Context, jobs <-chan Job) {
    defer close(w.done)
    for {
        select {
        case <-ctx.Done():
            return
        case job, ok := <-jobs:
            if !ok {
                return
            }
            process(job)
        }
    }
}

func (w *Worker) Stop() {
    w.cancel()
    <-w.done // wait for goroutine to finish
}
```

## Channel Patterns

```go
// Pipeline pattern: each stage reads from input, writes to output
func filter(ctx context.Context, in <-chan Order, predicate func(Order) bool) <-chan Order {
    out := make(chan Order)
    go func() {
        defer close(out)
        for order := range in {
            if predicate(order) {
                select {
                case out <- order:
                case <-ctx.Done():
                    return
                }
            }
        }
    }()
    return out
}

// Fan-out: distribute work to N workers
func fanOut(ctx context.Context, in <-chan Order, n int, process func(Order)) {
    var wg sync.WaitGroup
    for i := 0; i < n; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for order := range in {
                process(order)
            }
        }()
    }
    wg.Wait()
}
```

## sync.Mutex vs channels

| Use Case | Prefer |
|----------|--------|
| Protecting shared state | `sync.Mutex` / `sync.RWMutex` |
| Communicating between goroutines | Channels |
| One-time initialization | `sync.Once` |
| Wait for multiple goroutines | `sync.WaitGroup` |
| Rate limiting | Buffered channel as semaphore |

```go
// ✅ Mutex for protecting state
type SafeCache struct {
    mu    sync.RWMutex
    store map[string]Order
}

func (c *SafeCache) Get(key string) (Order, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    v, ok := c.store[key]
    return v, ok
}
```

## Always Run Tests with -race

```bash
go test -race ./...
```

The race detector catches data races at runtime. Always run it in CI.
