# Swift Standards

Swift is used for iOS, macOS, watchOS, and tvOS development.

## Quick Reference

| Rule | Value | Source |
|------|-------|--------|
| Line length | 100 characters | Google Swift Style Guide |
| Indentation | 2 spaces | Google Swift Style Guide |
| Naming: types | `UpperCamelCase` | Apple Swift API Design Guidelines |
| Naming: functions/vars | `lowerCamelCase` | Apple Swift API Design Guidelines |
| Trailing commas | Required in multi-line | Swift Style |
| `force unwrap` (`!`) | Never in production code | Team convention |
| `guard` | Use for early exits | Apple guidelines |
| Concurrency | `async/await` (Swift 5.5+) | Apple guidelines |

## Contents

| File | Topic |
|------|-------|
| [style-guide.md](style-guide.md) | Full formatting, naming, and code rules |
| [architecture.md](architecture.md) | MVVM, Clean Architecture for iOS |
| [testing.md](testing.md) | XCTest, Quick/Nimble conventions |
| [tooling.md](tooling.md) | SwiftLint, Xcode build settings |
| [examples/](examples/) | Good and bad Swift examples |
