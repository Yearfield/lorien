# PostgreSQL Migration Guide

This guide outlines the migration path from SQLite to PostgreSQL for production scalability and high-concurrency scenarios.

## Overview

While the current SQLite implementation with optimizations can handle moderate loads, PostgreSQL provides:

- **Better Concurrency**: True multi-writer support
- **Advanced Indexing**: GIN, GiST, partial indexes, expression indexes
- **Replication**: Built-in streaming replication
- **Monitoring**: Comprehensive performance monitoring tools
- **Scalability**: Horizontal and vertical scaling options
- **ACID Compliance**: Enhanced transaction isolation levels

## Migration Strategy

### Phase 1: Dual Database Support (Recommended)

Implement support for both SQLite and PostgreSQL to allow gradual migration:

```python
# api/db/database_factory.py
from enum import Enum
from typing import Protocol

class DatabaseType(Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"

class DatabaseRepository(Protocol):
    async def get_node_by_id(self, node_id: int) -> Optional[Dict[str, Any]]: ...
    async def get_children_by_parent_id(self, parent_id: int) -> List[Dict[str, Any]]: ...
    # ... other methods

def create_repository(db_type: DatabaseType) -> DatabaseRepository:
    if db_type == DatabaseType.SQLITE:
        return SQLiteRepository()
    elif db_type == DatabaseType.POSTGRESQL:
        return PostgreSQLRepository()
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
```

### Phase 2: PostgreSQL Schema

Create optimized PostgreSQL schema:

```sql
-- storage/postgresql_schema.sql
-- PostgreSQL schema for decision tree application

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Nodes table with optimized types
CREATE TABLE nodes (
    id         SERIAL PRIMARY KEY,
    parent_id  INTEGER NULL REFERENCES nodes(id) ON DELETE CASCADE,
    depth      INTEGER NOT NULL CHECK (depth BETWEEN 0 AND 6),
    slot       INTEGER NULL CHECK (
                   (parent_id IS NULL AND slot IS NULL AND depth = 0) OR
                   (parent_id IS NOT NULL AND slot IS NOT NULL AND slot >= 1 AND depth BETWEEN 1 AND 6)
               ),
    label      TEXT NOT NULL,
    is_leaf    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CHECK ( (depth = 0 AND parent_id IS NULL) OR (depth > 0 AND parent_id IS NOT NULL) )
);

-- Triage table
CREATE TABLE triage (
    node_id           INTEGER PRIMARY KEY REFERENCES nodes(id) ON DELETE CASCADE,
    diagnostic_triage TEXT,
    actions           TEXT,
    created_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Red flags table
CREATE TABLE red_flags (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    severity    severity_level NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create custom type for severity
CREATE TYPE severity_level AS ENUM ('low', 'medium', 'high', 'critical');

-- Tree parent version tracking
CREATE TABLE tree_parent_version (
    parent_id  INTEGER PRIMARY KEY REFERENCES nodes(id) ON DELETE CASCADE,
    version    INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Audit log
CREATE TABLE red_flag_audit (
    id         SERIAL PRIMARY KEY,
    node_id    INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    flag_id    INTEGER NOT NULL REFERENCES red_flags(id) ON DELETE CASCADE,
    action     action_type NOT NULL,
    timestamp  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TYPE action_type AS ENUM ('assigned', 'removed');

-- Performance optimized indexes
CREATE INDEX CONCURRENTLY idx_nodes_parent_id ON nodes(parent_id) WHERE parent_id IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_nodes_depth ON nodes(depth);
CREATE INDEX CONCURRENTLY idx_nodes_parent_slot ON nodes(parent_id, slot) WHERE parent_id IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_nodes_is_leaf ON nodes(is_leaf);

-- Composite indexes
CREATE INDEX CONCURRENTLY idx_nodes_depth_parent ON nodes(depth, parent_id);
CREATE INDEX CONCURRENTLY idx_nodes_parent_depth ON nodes(parent_id, depth);

-- Full-text search index
CREATE INDEX CONCURRENTLY idx_nodes_label_fts ON nodes USING gin(to_tsvector('english', label));

-- Covering indexes
CREATE INDEX CONCURRENTLY idx_nodes_children_covering ON nodes(parent_id, slot) INCLUDE (id, label, depth, is_leaf) WHERE parent_id IS NOT NULL;

-- Partial indexes for optimization
CREATE INDEX CONCURRENTLY idx_nodes_incomplete_parents ON nodes(id, depth, parent_id) WHERE depth < 5 AND parent_id IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_nodes_root ON nodes(id, label) WHERE depth = 0;

-- Time-based indexes
CREATE INDEX CONCURRENTLY idx_nodes_created_at ON nodes(created_at);
CREATE INDEX CONCURRENTLY idx_nodes_updated_at ON nodes(updated_at);
CREATE INDEX CONCURRENTLY idx_triage_updated_at ON triage(updated_at);
CREATE INDEX CONCURRENTLY idx_red_flag_audit_timestamp ON red_flag_audit(timestamp);

-- Triggers for automatic updates
CREATE OR REPLACE FUNCTION update_is_leaf()
RETURNS TRIGGER AS $$
BEGIN
    NEW.is_leaf = (NEW.depth >= 5);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_is_leaf_trigger
    BEFORE INSERT OR UPDATE OF depth ON nodes
    FOR EACH ROW
    EXECUTE FUNCTION update_is_leaf();

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_timestamp_trigger
    BEFORE UPDATE ON nodes
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_triage_timestamp_trigger
    BEFORE UPDATE ON triage
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Views for common queries
CREATE VIEW nodes_with_parent AS
SELECT
    n.id,
    n.parent_id,
    n.depth,
    n.slot,
    n.label,
    n.is_leaf,
    n.created_at,
    n.updated_at,
    p.label as parent_label,
    p.depth as parent_depth
FROM nodes n
LEFT JOIN nodes p ON n.parent_id = p.id;

CREATE VIEW incomplete_parents AS
SELECT
    n.id,
    n.label,
    n.depth,
    n.parent_id,
    COUNT(c.id) as child_count,
    (5 - COUNT(c.id)) as slots_available
FROM nodes n
LEFT JOIN nodes c ON n.id = c.parent_id
WHERE n.depth < 5 AND n.parent_id IS NOT NULL
GROUP BY n.id, n.label, n.depth, n.parent_id
HAVING COUNT(c.id) < 5
ORDER BY n.id;

-- Performance monitoring
CREATE VIEW query_performance AS
SELECT
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY total_time DESC;

-- Enable query statistics
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET pg_stat_statements.track = 'all';
```

### Phase 3: PostgreSQL Repository Implementation

```python
# api/db/postgresql_repo.py
import asyncpg
import asyncio
from typing import Any, Dict, List, Optional, Tuple
from api.db.connection_pool import AsyncPGPool

class PostgreSQLRepository:
    """PostgreSQL repository implementation."""

    def __init__(self, pool: AsyncPGPool):
        self.pool = pool

    async def get_node_by_id(self, node_id: int) -> Optional[Dict[str, Any]]:
        """Get node by ID with caching."""
        query = """
            SELECT id, parent_id, depth, slot, label, is_leaf,
                   created_at, updated_at
            FROM nodes
            WHERE id = $1
        """

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, node_id)
            return dict(row) if row else None

    async def get_children_by_parent_id(self, parent_id: int) -> List[Dict[str, Any]]:
        """Get children with optimized query."""
        query = """
            SELECT id, parent_id, depth, slot, label, is_leaf,
                   created_at, updated_at
            FROM nodes
            WHERE parent_id = $1
            ORDER BY slot ASC
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, parent_id)
            return [dict(row) for row in rows]

    async def search_nodes(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Full-text search using PostgreSQL FTS."""
        query = """
            SELECT id, parent_id, depth, slot, label, is_leaf,
                   created_at, updated_at,
                   ts_rank(to_tsvector('english', label), plainto_tsquery('english', $1)) as rank
            FROM nodes
            WHERE to_tsvector('english', label) @@ plainto_tsquery('english', $1)
            ORDER BY rank DESC, label ASC
            LIMIT $2
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, search_term, limit)
            return [dict(row) for row in rows]

    async def get_tree_statistics(self) -> Dict[str, Any]:
        """Get comprehensive tree statistics."""
        queries = {
            'total_nodes': "SELECT COUNT(*) as count FROM nodes",
            'nodes_by_depth': """
                SELECT depth, COUNT(*) as count
                FROM nodes
                GROUP BY depth
                ORDER BY depth
            """,
            'leaf_nodes': "SELECT COUNT(*) as count FROM nodes WHERE is_leaf = true",
            'triage_count': "SELECT COUNT(*) as count FROM triage",
            'red_flags_count': "SELECT COUNT(*) as count FROM red_flags"
        }

        stats = {}
        async with self.pool.acquire() as conn:
            for stat_name, query in queries.items():
                if stat_name == 'nodes_by_depth':
                    rows = await conn.fetch(query)
                    stats[stat_name] = [dict(row) for row in rows]
                else:
                    row = await conn.fetchrow(query)
                    stats[stat_name] = dict(row)['count'] if row else 0

        return stats
```

### Phase 4: Connection Pool for PostgreSQL

```python
# api/db/postgresql_pool.py
import asyncpg
import asyncio
from typing import Optional

class AsyncPGPool:
    """PostgreSQL connection pool wrapper."""

    def __init__(self, connection_string: str, min_connections: int = 5, max_connections: int = 20):
        self.connection_string = connection_string
        self.min_connections = min_connections
        self.max_connections = max_connections
        self._pool: Optional[asyncpg.Pool] = None

    async def initialize(self):
        """Initialize the connection pool."""
        self._pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=self.min_connections,
            max_size=self.max_connections,
            command_timeout=60,
            server_settings={
                'application_name': 'lorien',
                'timezone': 'UTC'
            }
        )

    async def close(self):
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()

    def acquire(self):
        """Acquire a connection from the pool."""
        if not self._pool:
            raise RuntimeError("Pool not initialized")
        return self._pool.acquire()
```

## Migration Process

### 1. Data Migration Script

```python
# scripts/migrate_to_postgresql.py
import asyncio
import sqlite3
import asyncpg
from pathlib import Path

async def migrate_data(sqlite_path: str, postgres_url: str):
    """Migrate data from SQLite to PostgreSQL."""

    # Connect to both databases
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row

    postgres_pool = await asyncpg.create_pool(postgres_url)

    try:
        async with postgres_pool.acquire() as pg_conn:
            # Migrate nodes
            sqlite_cursor = sqlite_conn.execute("SELECT * FROM nodes ORDER BY id")
            nodes_data = sqlite_cursor.fetchall()

            for node in nodes_data:
                await pg_conn.execute("""
                    INSERT INTO nodes (id, parent_id, depth, slot, label, is_leaf, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (id) DO NOTHING
                """,
                node['id'], node['parent_id'], node['depth'],
                node['slot'], node['label'], bool(node['is_leaf']),
                node['created_at'], node['updated_at']
                )

            # Migrate triage data
            sqlite_cursor = sqlite_conn.execute("SELECT * FROM triage")
            triage_data = sqlite_cursor.fetchall()

            for triage in triage_data:
                await pg_conn.execute("""
                    INSERT INTO triage (node_id, diagnostic_triage, actions, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (node_id) DO NOTHING
                """,
                triage['node_id'], triage['diagnostic_triage'],
                triage['actions'], triage['created_at'], triage['updated_at']
                )

            # Migrate red flags
            sqlite_cursor = sqlite_conn.execute("SELECT * FROM red_flags")
            red_flags_data = sqlite_cursor.fetchall()

            for flag in red_flags_data:
                await pg_conn.execute("""
                    INSERT INTO red_flags (id, name, description, severity, created_at)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (id) DO NOTHING
                """,
                flag['id'], flag['name'], flag['description'],
                flag['severity'], flag['created_at']
                )

            print(f"Migration completed successfully")

    finally:
        sqlite_conn.close()
        await postgres_pool.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python migrate_to_postgresql.py <sqlite_path> <postgres_url>")
        sys.exit(1)

    asyncio.run(migrate_data(sys.argv[1], sys.argv[2]))
```

### 2. Configuration Updates

```python
# api/settings.py
import os
from enum import Enum

class DatabaseType(Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"

def get_database_type() -> DatabaseType:
    """Get database type from environment."""
    db_type = os.getenv("LORIEN_DATABASE_TYPE", "sqlite").lower()
    if db_type == "postgresql":
        return DatabaseType.POSTGRESQL
    return DatabaseType.SQLITE

def get_postgresql_url() -> str:
    """Get PostgreSQL connection URL."""
    return os.getenv(
        "LORIEN_POSTGRESQL_URL",
        "postgresql://lorien:password@localhost:5432/lorien"  # pragma: allowlist secret
    )

def get_postgresql_pool_config() -> dict:
    """Get PostgreSQL pool configuration."""
    return {
        "min_connections": int(os.getenv("LORIEN_PG_MIN_CONNECTIONS", "5")),
        "max_connections": int(os.getenv("LORIEN_PG_MAX_CONNECTIONS", "20")),
        "connection_timeout": float(os.getenv("LORIEN_PG_TIMEOUT", "30.0"))
    }
```

### 3. Environment Configuration

```bash
# .env.postgresql
LORIEN_DATABASE_TYPE=postgresql
LORIEN_POSTGRESQL_URL=postgresql://lorien:password@localhost:5432/lorien
LORIEN_PG_MIN_CONNECTIONS=5
LORIEN_PG_MAX_CONNECTIONS=20
LORIEN_PG_TIMEOUT=30.0

# Performance tuning
LORIEN_CACHE_SIZE_MB=200
LORIEN_CACHE_TTL_SECONDS=600
LORIEN_SLOW_QUERY_THRESHOLD=50.0
```

## Performance Benefits

### Expected Improvements

1. **Concurrency**: 10-100x improvement in concurrent write operations
2. **Query Performance**: 2-5x improvement for complex queries
3. **Memory Usage**: Better memory management and shared buffers
4. **Monitoring**: Built-in performance monitoring and statistics
5. **Replication**: Built-in streaming replication for high availability

### Monitoring and Tuning

```sql
-- Performance monitoring queries
SELECT * FROM pg_stat_activity WHERE state = 'active';
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
SELECT * FROM pg_stat_database WHERE datname = 'lorien';

-- Index usage statistics
SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_tup_read DESC;
```

## Deployment Considerations

### Docker Configuration

```dockerfile
# Dockerfile.postgresql
FROM python:3.11-slim

# Install PostgreSQL client
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Environment variables
ENV LORIEN_DATABASE_TYPE=postgresql
ENV LORIEN_POSTGRESQL_URL=postgresql://lorien:password@postgres:5432/lorien

# Run application
CMD ["python", "-m", "api.main"]
```

```yaml
# docker-compose.postgresql.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: lorien
      POSTGRES_USER: lorien
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./storage/postgresql_schema.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    command: >
      postgres
      -c shared_preload_libraries=pg_stat_statements
      -c track_activity_query_size=2048
      -c pg_stat_statements.track=all
      -c max_connections=100
      -c shared_buffers=256MB
      -c effective_cache_size=1GB

  app:
    build:
      context: .
      dockerfile: Dockerfile.postgresql
    environment:
      LORIEN_DATABASE_TYPE: postgresql
      LORIEN_POSTGRESQL_URL: postgresql://lorien:password@postgres:5432/lorien
    depends_on:
      - postgres
    ports:
      - "8000:8000"

volumes:
  postgres_data:
```

## Migration Checklist

- [ ] Set up PostgreSQL development environment
- [ ] Implement PostgreSQL repository layer
- [ ] Create data migration scripts
- [ ] Update configuration management
- [ ] Implement connection pooling for PostgreSQL
- [ ] Add performance monitoring for PostgreSQL
- [ ] Create deployment configurations
- [ ] Test migration process with production data backup
- [ ] Update documentation and runbooks
- [ ] Plan rollback strategy
- [ ] Performance testing and benchmarking
- [ ] Security review and hardening

## Rollback Strategy

1. **Database Switch**: Use environment variable to switch back to SQLite
2. **Data Export**: Export PostgreSQL data to SQLite format if needed
3. **Connection Pooling**: Graceful shutdown of PostgreSQL connections
4. **Monitoring**: Switch monitoring back to SQLite-specific metrics

This migration path allows for gradual adoption while maintaining backward compatibility and providing a clear rollback strategy.
