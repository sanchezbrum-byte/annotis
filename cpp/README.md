# C++ Standards

C++ is used for performance-critical services, systems programming, game engines, and embedded systems.

## Quick Reference

| Rule | Value | Source |
|------|-------|--------|
| Line length | 80 characters | Google C++ Style Guide |
| Indentation | 2 spaces | Google C++ Style Guide |
| Header guards | `#pragma once` (or `#ifndef` guard) | Google C++ Style Guide |
| File extension | `.cc` for source, `.h` for headers | Google C++ Style Guide |
| Naming: functions | `CamelCase()` | Google C++ Style Guide |
| Naming: variables | `snake_case` | Google C++ Style Guide |
| Naming: constants | `kCamelCase` | Google C++ Style Guide |
| Naming: classes | `PascalCase` | Google C++ Style Guide |
| Smart pointers | Use `unique_ptr` / `shared_ptr`; never raw `new`/`delete` | C++ Core Guidelines |
| Exceptions | Project-dependent; document the policy | Google disables exceptions |

## Contents

| File | Topic |
|------|-------|
| [style-guide.md](style-guide.md) | Full formatting, naming, and code rules |
| [memory-management.md](memory-management.md) | RAII, smart pointers, ownership |
| [architecture.md](architecture.md) | Project layout, interface patterns |
| [testing.md](testing.md) | Google Test / Catch2 conventions |
| [performance.md](performance.md) | Profiling, optimization patterns |
| [examples/](examples/) | Good and bad C++ examples |
