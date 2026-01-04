# Rust API Key Generation Pattern

## When to Use
Any task involving API key generation, storage, or validation for scanner authentication.

## Pattern

### Key Generation (CSPRNG)

```rust
use rand::rngs::OsRng;
use rand::RngCore;
use sha2::{Sha256, Digest};
use secrecy::{Secret, ExposeSecret};

pub struct ApiKey {
    key: Secret<String>,
    prefix: String,
    hash: String,
}

impl ApiKey {
    /// Generate a new API key with 32 bytes of cryptographic randomness
    pub fn generate() -> Self {
        let mut bytes = [0u8; 32];
        OsRng.fill_bytes(&mut bytes);

        let key = hex::encode(bytes);
        let prefix = format!("argus_sk_{}", &key[..8]);
        let hash = Self::compute_hash(&key);

        Self {
            key: Secret::new(key),
            prefix,
            hash,
        }
    }

    fn compute_hash(key: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(key.as_bytes());
        hex::encode(hasher.finalize())
    }

    /// Expose the full key - ONLY call this once at creation time
    pub fn expose_once(&self) -> &str {
        self.key.expose_secret()
    }

    pub fn prefix(&self) -> &str {
        &self.prefix
    }

    pub fn hash(&self) -> &str {
        &self.hash
    }
}
```

### Constant-Time Validation

```rust
use subtle::ConstantTimeEq;

impl ApiKey {
    /// Validate a key against a stored hash using constant-time comparison
    pub fn validate(key: &str, stored_hash: &str) -> bool {
        let computed = Self::compute_hash(key);
        computed.as_bytes().ct_eq(stored_hash.as_bytes()).into()
    }
}
```

### Key Prefix Format

```
argus_sk_a1b2c3d4  (visible to user)
         ^^^^^^^^
         first 8 chars of full key
```

### Secret Reference Format

```rust
/// Format: {provider}:{path}
/// Examples:
/// - aws:argus/scanner-keys/{id}
/// - vault:secret/argus/keys/{id}
/// - env:SCANNER_KEY_{id}
pub fn format_secret_ref(provider: &str, id: &Uuid) -> String {
    match provider {
        "aws" => format!("aws:argus/scanner-keys/{}", id),
        "vault" => format!("vault:secret/argus/keys/{}", id),
        _ => format!("{}:argus/keys/{}", provider, id),
    }
}
```

## Anti-Patterns

| Don't Do | Why | Do Instead |
|----------|-----|------------|
| `rand::thread_rng()` for keys | Not cryptographically secure | Use `OsRng` |
| Store plaintext keys | Security breach exposure | Store only SHA-256 hash |
| Log full API key | Key exposure in logs | Log only prefix |
| `==` for hash comparison | Timing attack vulnerability | Use `subtle::ConstantTimeEq` |
| Return key multiple times | Increases exposure risk | Return only once at creation |

## Examples in Codebase
- `submodules/argus-common/src/auth/api_key.rs`
- `submodules/argus-api/src/handlers/scanner.rs`
