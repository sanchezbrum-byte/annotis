# Java Tooling

## Required Tools

| Tool | Purpose | Config |
|------|---------|--------|
| **Maven** or **Gradle** | Build tool | `pom.xml` or `build.gradle.kts` |
| **Google Java Format** | Auto-formatter | Maven/Gradle plugin |
| **Checkstyle** | Style linting | `checkstyle.xml` (Google config) |
| **SpotBugs** | Static analysis | Maven/Gradle plugin |
| **JaCoCo** | Coverage | Maven/Gradle plugin |
| **Flyway** | Database migrations | Spring Boot auto-config |

## Gradle (Preferred for new projects)

```kotlin
// build.gradle.kts
plugins {
  java
  id("org.springframework.boot") version "3.2.4"
  id("io.spring.dependency-management") version "1.1.4"
  id("com.diffplug.spotless") version "6.25.0"
  id("checkstyle")
  jacoco
}

java {
  sourceCompatibility = JavaVersion.VERSION_21
}

spotless {
  java {
    googleJavaFormat("1.22.0")
    removeUnusedImports()
    trimTrailingWhitespace()
  }
}

jacoco {
  toolVersion = "0.8.11"
}

tasks.jacocoTestReport {
  reports { xml.required.set(true) }
}

tasks.jacocoTestCoverageVerification {
  violationRules {
    rule {
      limit {
        minimum = "0.80".toBigDecimal()
      }
    }
  }
}
```

## CI Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '21', distribution: 'temurin' }
      - run: ./gradlew spotlessCheck checkstyleMain test jacocoTestCoverageVerification
```
