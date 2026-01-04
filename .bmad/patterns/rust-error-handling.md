# Rust Error Handling Pattern

## When to Use
All Rust code that can fail - API handlers, database operations, external service calls.

## Pattern

### Error Type Definition

```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum DomainError {
    #[error("Not found: {0}")]
    NotFound(String),

    #[error("Validation failed: {0}")]
    Validation(String),

    #[error("Unauthorized: {0}")]
    Unauthorized(String),

    #[error("Database error: {0}")]
    Database(#[from] clickhouse::error::Error),

    #[error("Internal error: {0}")]
    Internal(String),
}
```

### Result Type Alias

```rust
pub type Result<T> = std::result::Result<T, DomainError>;
```

### API Response Mapping

```rust
impl axum::response::IntoResponse for DomainError {
    fn into_response(self) -> axum::response::Response {
        let (status, message) = match &self {
            DomainError::NotFound(msg) => (StatusCode::NOT_FOUND, msg.clone()),
            DomainError::Validation(msg) => (StatusCode::BAD_REQUEST, msg.clone()),
            DomainError::Unauthorized(msg) => (StatusCode::UNAUTHORIZED, msg.clone()),
            DomainError::Database(_) => (StatusCode::INTERNAL_SERVER_ERROR, "Database error".into()),
            DomainError::Internal(msg) => (StatusCode::INTERNAL_SERVER_ERROR, msg.clone()),
        };

        let body = Json(json!({ "error": message }));
        (status, body).into_response()
    }
}
```

### Usage in Handlers

```rust
pub async fn get_finding(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
) -> Result<Json<Finding>> {
    let finding = state.db
        .get_finding(id)
        .await?
        .ok_or_else(|| DomainError::NotFound(format!("Finding {id} not found")))?;

    Ok(Json(finding))
}
```

## Anti-Patterns

| Don't Do | Why | Do Instead |
|----------|-----|------------|
| `unwrap()` in production code | Panics on error | Use `?` operator or explicit handling |
| Generic `anyhow::Error` in public APIs | Loses type information | Define domain-specific errors |
| Logging sensitive data in errors | Security risk | Sanitize error messages |
| Catching all errors with `_` | Hides bugs | Match specific variants |

## Examples in Codebase
- `submodules/argus-common/src/error.rs`
- `submodules/argus-api/src/error.rs`
