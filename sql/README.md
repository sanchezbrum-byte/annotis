# SQL Standards

SQL standards apply to all database interactions — query writing, schema design, and migrations.

## Quick Reference

| Rule | Value | Source |
|------|-------|--------|
| Keywords | UPPERCASE | GitLab SQL Style Guide, dbt Style Guide |
| Table/column names | `snake_case` | dbt Style Guide |
| Indentation | 4 spaces | GitLab SQL Style Guide |
| Line limit | 120 characters (soft) | Team convention |
| Trailing commas | Leading commas (dbt style) OR trailing — pick one, be consistent | |
| Aliases | Always use `AS` keyword | GitLab SQL Style Guide |
| Boolean columns | `is_` prefix | dbt Style Guide |
| Migration tool | Flyway (Java) / Alembic (Python) / golang-migrate (Go) | |

## Contents

| File | Topic |
|------|-------|
| [style-guide.md](style-guide.md) | Query formatting, naming, and code rules |
| [query-optimization.md](query-optimization.md) | Indexes, EXPLAIN, query patterns |
| [schema-design.md](schema-design.md) | Table design, normalization, constraints |
| [migrations.md](migrations.md) | Safe migration patterns |
| [examples/](examples/) | Good and bad SQL examples |
