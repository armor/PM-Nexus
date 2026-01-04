# Backend Service Story Template

> **Template Type:** Backend/Engineering (Rust Services)
> **Applies To:** API endpoints, services, data models, business logic

---

## Pre-filled Sections for Backend Stories

### Architecture Context (copy to Problem Statement)
```
SERVICE ARCHITECTURE:
┌─────────────────────────────────────────────────────────────────────────────┐
│ argus-api (8080) ─► argus-{{SERVICE}} ({{PORT}}) ─► {{DOWNSTREAM}}         │
│      │                      │                                               │
│      ▼                      ▼                                               │
│ ClickHouse             OpenTelemetry ─► SigNoz                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Standard Dependencies (Cargo.toml)
```toml
[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter", "json"] }
opentelemetry = "0.21"
opentelemetry-otlp = "0.14"
opentelemetry_sdk = { version = "0.21", features = ["rt-tokio"] }
tracing-opentelemetry = "0.22"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
config = "0.14"
thiserror = "1"
uuid = { version = "1", features = ["v4", "serde"] }
chrono = { version = "0.4", features = ["serde"] }
```

### Standard Directory Structure
```
submodules/argus-{{service}}/
├── Cargo.toml
├── src/
│   ├── main.rs
│   ├── lib.rs
│   ├── config.rs
│   ├── telemetry.rs
│   ├── error.rs
│   ├── handlers/
│   │   ├── mod.rs
│   │   └── {{handler}}.rs
│   └── domain/
│       ├── mod.rs
│       └── {{entity}}.rs
└── tests/
    └── integration_test.rs
```

### Standard Quality Checks
```bash
# MUST pass for every backend story
cargo fmt -p {{package}} --check
cargo clippy -p {{package}} -- -D warnings
cargo test -p {{package}}
```

### Standard API Handler Pattern
```rust
use axum::{extract::State, http::StatusCode, Json};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize)]
pub struct {{Response}}Response {
    // fields
}

#[derive(Debug, Deserialize)]
pub struct {{Request}}Request {
    // fields
}

#[tracing::instrument(name = "{{handler_name}}", skip(state))]
pub async fn {{handler_name}}(
    State(state): State<AppState>,
    Json(request): Json<{{Request}}Request>,
) -> Result<Json<{{Response}}Response>, AppError> {
    tracing::info!("Processing {{handler_name}}");

    // Implementation

    Ok(Json({{Response}}Response { /* fields */ }))
}
```

### Standard Test Pattern
```rust
#[cfg(test)]
mod tests {
    use super::*;
    use axum::http::StatusCode;

    #[tokio::test]
    async fn test_{{handler}}_success() {
        // Arrange
        let request = {{Request}}Request { /* fields */ };

        // Act
        let result = {{handler_name}}(/* args */).await;

        // Assert
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_{{handler}}_invalid_input() {
        // Test error case
    }
}
```

### Standard Integration Test Pattern
```rust
use axum::{body::Body, http::{Request, StatusCode}};
use tower::ServiceExt;

#[tokio::test]
async fn test_{{endpoint}}_integration() {
    let app = create_test_app();

    let response = app
        .oneshot(
            Request::builder()
                .method("{{METHOD}}")
                .uri("{{PATH}}")
                .header("content-type", "application/json")
                .body(Body::from(r#"{"field": "value"}"#))
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::OK);
}
```

### Standard Config Pattern
```rust
use config::{Config, ConfigError, Environment};
use serde::Deserialize;

#[derive(Debug, Deserialize, Clone)]
pub struct Settings {
    pub service_port: u16,
    pub otel_endpoint: String,
    #[serde(default = "default_service_name")]
    pub service_name: String,
}

fn default_service_name() -> String {
    "argus-{{service}}".to_string()
}

impl Settings {
    pub fn new() -> Result<Self, ConfigError> {
        Config::builder()
            .add_source(Environment::default().separator("__"))
            .build()?
            .try_deserialize()
    }
}
```

---

## Backend Story AI Prompt Template

```
IMPLEMENT {{STORY_ID}}: {{STORY_TITLE}}

CONTEXT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You are adding {{WHAT}} to {{SERVICE}} in Armor Argus.
This service handles {{SERVICE_PURPOSE}}.

TARGET FILES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. {{FILE_1}}: {{PURPOSE_1}}
2. {{FILE_2}}: {{PURPOSE_2}}
3. {{FILE_3}}: {{PURPOSE_3}}

PATTERNS TO FOLLOW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reference: {{REFERENCE_FILE}} for {{PATTERN_TYPE}}

IMPLEMENTATION STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. {{STEP_1}}
2. {{STEP_2}}
3. {{STEP_3}}
4. Add unit tests
5. Add integration tests
6. Verify with: {{VERIFY_COMMAND}}

EXACT CODE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{{EXACT_CODE_BLOCK}}

VERIFICATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cargo build -p {{package}}
cargo test -p {{package}}
cargo run -p {{package}} &
curl -X {{METHOD}} http://localhost:{{PORT}}{{PATH}}
# Expected: {{EXPECTED_RESPONSE}}

PROHIBITED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- No unwrap() on Results - use ? or explicit handling
- No println! - use tracing::{info, debug, error}
- No hardcoded values - use config
- No TODO/FIXME without issue link
```
