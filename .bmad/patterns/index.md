# Code Patterns Library

> **Centralized patterns for consistent implementation across tasks**

## Purpose

This directory contains reusable code patterns that are referenced by task files. When multiple tasks need the same pattern, reference it here instead of duplicating.

---

## MANDATORY STANDARDS (ALL TASKS)

### 1. Four-Path Unit Testing

Every function MUST have tests covering:

| Path | Description | Required |
|------|-------------|----------|
| **Happy Path** | Valid inputs → expected output | YES |
| **Fail Path** | Invalid inputs → proper errors | YES |
| **Null/Empty Path** | Null, None, empty values handled | YES |
| **Edge Cases** | Boundaries, concurrent access | YES |

### 2. Gang of Four Design Patterns

Use appropriate GoF patterns:
- **Factory**: Object creation without specifying class
- **Strategy**: Interchangeable algorithms (scanner adapters)
- **Adapter**: Interface compatibility
- **Observer**: Event notification
- **Builder**: Complex object construction
- **Template Method**: Algorithm skeleton

### 3. SOLID Principles

| Principle | Rule |
|-----------|------|
| **S**ingle Responsibility | One reason to change |
| **O**pen/Closed | Extend, don't modify |
| **L**iskov Substitution | Subtypes substitutable |
| **I**nterface Segregation | Small, focused interfaces |
| **D**ependency Inversion | Depend on abstractions |

### 4. DRY (Don't Repeat Yourself)

Extract common code into reusable functions/traits.

### 5. No Nested If Statements

Use guard clauses and early returns instead:

```rust
// WRONG - nested
if auth { if perm { if data { /* do */ } } }

// CORRECT - guard clauses
if !auth { return Err(Unauthenticated); }
if !perm { return Err(PermissionDenied); }
let data = get_data()?;
// do work
```

## How to Use

In task files, reference patterns like this:

```markdown
## Code Patterns

See: [rust-error-handling](../../../../../.bmad/patterns/rust-error-handling.md)
See: [clickhouse-schema](../../../../../.bmad/patterns/clickhouse-schema.md)
```

Or include inline with task-specific additions:

```markdown
## Code Patterns

### Base Pattern
See: [rust-api-key](../../../../../.bmad/patterns/rust-api-key.md)

### Task-Specific Additions
[additional patterns specific to this task]
```

---

## Pattern Index

### Rust Patterns

| Pattern | File | Used By |
|---------|------|---------|
| Error Handling | [rust-error-handling.md](./rust-error-handling.md) | All Rust tasks |
| API Key Generation | [rust-api-key.md](./rust-api-key.md) | AUTH-001-* tasks |
| Axum Handler | [rust-axum-handler.md](./rust-axum-handler.md) | API endpoint tasks |
| Domain Types | [rust-domain-types.md](./rust-domain-types.md) | Domain modeling tasks |
| Secrets Handling | [rust-secrets.md](./rust-secrets.md) | Security tasks |

### Database Patterns

| Pattern | File | Used By |
|---------|------|---------|
| ClickHouse Schema | [clickhouse-schema.md](./clickhouse-schema.md) | Migration tasks |
| ClickHouse Queries | [clickhouse-queries.md](./clickhouse-queries.md) | Data access tasks |
| NebulaGraph Schema | [nebulagraph-schema.md](./nebulagraph-schema.md) | Graph tasks |

### Testing Patterns

| Pattern | File | Used By |
|---------|------|---------|
| Rust Unit Tests | [rust-unit-tests.md](./rust-unit-tests.md) | All Rust test tasks |
| Integration Tests | [rust-integration-tests.md](./rust-integration-tests.md) | Integration tasks |

---

## Adding New Patterns

1. Create new file: `.bmad/patterns/{category}-{name}.md`
2. Use template below
3. Add to index table above
4. Update tasks that use this pattern to reference it

### Pattern Template

```markdown
# {Pattern Name}

## When to Use
{Brief description of when this pattern applies}

## Pattern

\`\`\`{language}
{code pattern}
\`\`\`

## Variations

### {Variation 1}
{variation code}

## Anti-Patterns

| Don't Do | Why | Do Instead |
|----------|-----|------------|
| | | |

## Examples in Codebase
- `{file_path_1}`
- `{file_path_2}`
```

---

## Maintenance

When code review finds issues with a pattern:
1. Update the pattern file
2. Add to Anti-Patterns section
3. Note in "Pattern History" at bottom of file

---

**Version:** 1.0
**Last Updated:** 2026-01-02
