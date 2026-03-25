# Kotlin Standards

Kotlin is used for Android development and JVM backend services (Ktor, Spring Boot).

## Quick Reference

| Rule | Value | Source |
|------|-------|--------|
| Line length | 120 characters | Kotlin Coding Conventions |
| Indentation | 4 spaces | Kotlin Coding Conventions |
| Naming: classes | `PascalCase` | Kotlin Coding Conventions |
| Naming: functions/vars | `camelCase` | Kotlin Coding Conventions |
| Naming: constants | `UPPER_SNAKE_CASE` | Kotlin Coding Conventions |
| Trailing commas | Optional but recommended | Kotlin Coding Conventions |
| Null safety | Use `?` and `?.` — avoid `!!` | Kotlin best practices |
| Coroutines | `suspend fun` + structured concurrency | Kotlin Coroutines guide |

## Contents

| File | Topic |
|------|-------|
| [style-guide.md](style-guide.md) | Full formatting, naming, and code rules |
| [coroutines.md](coroutines.md) | Coroutines, Flow, structured concurrency |
| [architecture.md](architecture.md) | MVVM, Clean Architecture for Android/Ktor |
| [testing.md](testing.md) | JUnit 5, MockK, Kotest conventions |
| [examples/](examples/) | Good and bad Kotlin examples |
