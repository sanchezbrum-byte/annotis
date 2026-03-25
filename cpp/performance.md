# C++ Performance

---

## Profile First

```bash
# Compile with profiling
g++ -O2 -pg -o myapp main.cc
./myapp
gprof myapp gmon.out | head -30

# Linux perf
perf record -g ./myapp
perf report

# Valgrind for memory profiling
valgrind --tool=massif ./myapp
ms_print massif.out.* | head -50
```

## Key Performance Patterns

### Avoid Unnecessary Copies

```cpp
// ❌ BAD: copies the entire string
std::string GetName() { return name_; }  // copy on return
void SetName(std::string name) { name_ = name; }  // copies again

// ✅ GOOD: return reference; accept by value + move
const std::string& GetName() const { return name_; }
void SetName(std::string name) { name_ = std::move(name); }
```

### Reserve Container Capacity

```cpp
// ❌ BAD: O(n log n) reallocations
std::vector<Order> orders;
for (const auto& item : raw_items) {
  orders.push_back(transform(item));  // may reallocate
}

// ✅ GOOD: reserve first — O(n) single allocation
std::vector<Order> orders;
orders.reserve(raw_items.size());
for (const auto& item : raw_items) {
  orders.emplace_back(transform(item));
}
```

### Cache-Friendly Data Layout

```cpp
// ❌ BAD: Array of Structures — poor cache utilization for position-only loops
struct Particle { float x, y, z, vx, vy, vz, mass; };
std::vector<Particle> particles;  // accessing x,y,z skips vx,vy,vz,mass

// ✅ GOOD: Structure of Arrays — excellent cache utilization for SIMD
struct ParticleSystem {
  std::vector<float> x, y, z;      // positions
  std::vector<float> vx, vy, vz;   // velocities
  std::vector<float> mass;
};
```

### Big-O Comment for Non-Trivial Algorithms

```cpp
// Merge k sorted lists
// Time: O(N log k) where N = total elements, k = number of lists
// Space: O(k) for the priority queue
std::vector<int> MergeKSortedLists(const std::vector<std::vector<int>>& lists) { ... }
```
