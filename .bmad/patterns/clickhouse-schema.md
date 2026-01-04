# ClickHouse Schema Pattern

## When to Use
Any task creating or modifying ClickHouse tables, migrations, or queries.

## Pattern

### Table Creation

```sql
CREATE TABLE {table_name} (
    -- Primary identifiers
    id UUID DEFAULT generateUUIDv4(),
    account_id UUID NOT NULL,

    -- Domain fields
    {domain_fields}

    -- Enum fields (use Enum8 for <256 values)
    status Enum8('pending'=1, 'active'=2, 'completed'=3, 'failed'=4),

    -- Timestamps (use DateTime64 for precision)
    created_at DateTime64(3) DEFAULT now64(),
    updated_at DateTime64(3) DEFAULT now64(),

    -- Soft delete
    deleted_at DateTime64(3),

    -- Bloom filter indexes for high-cardinality lookups
    INDEX idx_{field} ({field}) TYPE bloom_filter GRANULARITY 1

) ENGINE = MergeTree()
ORDER BY (account_id, id)
PARTITION BY toYYYYMM(created_at)
TTL created_at + INTERVAL 90 DAY;
```

### Enum Definition

```sql
-- Scanner types (14 values)
scanner_type Enum8(
    'prowler'=1, 'trivy'=2, 'grype'=3, 'falco'=4,
    'clair'=5, 'scoutsuite'=6, 'steampipe'=7,
    'cartography'=8, 'cloudmapper'=9, 'cloudsplaining'=10,
    'pmapper'=11, 'iam_visualizer'=12, 'cloud_custodian'=13,
    'wazuh_adapter'=14
),

-- Cloud providers
cloud_provider Enum8('aws'=1, 'azure'=2, 'gcp'=3, 'oci'=4, 'multi'=5),

-- Severity levels
severity Enum8('critical'=1, 'high'=2, 'medium'=3, 'low'=4, 'info'=5),
```

### Index Patterns

```sql
-- Bloom filter for exact matches on high-cardinality columns
INDEX idx_account (account_id) TYPE bloom_filter GRANULARITY 1,
INDEX idx_key_hash (key_hash) TYPE bloom_filter GRANULARITY 1,

-- Set index for array columns
INDEX idx_labels (labels) TYPE set(100) GRANULARITY 1,

-- MinMax for range queries
INDEX idx_created (created_at) TYPE minmax GRANULARITY 1,
```

### Migration File Structure

```sql
-- migrations/001_create_{table_name}.sql

-- Up migration
CREATE TABLE IF NOT EXISTS {table_name} (
    ...
) ENGINE = MergeTree()
...;

-- Verification query
-- SELECT count() FROM system.tables WHERE name = '{table_name}';
```

### Materialized View

```sql
CREATE MATERIALIZED VIEW {view_name}
ENGINE = SummingMergeTree()
ORDER BY (account_id, date)
AS SELECT
    account_id,
    toDate(created_at) as date,
    severity,
    count() as count
FROM findings
GROUP BY account_id, date, severity;
```

## Anti-Patterns

| Don't Do | Why | Do Instead |
|----------|-----|------------|
| `String` for enums | Wastes space, no validation | Use `Enum8` or `Enum16` |
| `DateTime` without precision | Millisecond loss | Use `DateTime64(3)` |
| Skip indexes on filter columns | Slow queries at scale | Add Bloom filter indexes |
| Hard delete | Audit trail loss | Use soft delete with `deleted_at` |
| No partitioning | Unbounded table growth | Partition by month + TTL |
| `SELECT *` | Network overhead | Select specific columns |

## Examples in Codebase
- `submodules/argus-common/migrations/001_scanner_api_keys.sql`
- `submodules/argus-common/migrations/002_findings.sql`
