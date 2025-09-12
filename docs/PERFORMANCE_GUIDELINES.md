# Performance Guidelines

This document outlines performance requirements, benchmarks, and optimization strategies for the Lorien application.

## Performance Requirements

### Response Time Targets

- **Navigate queries**: p95 < 150ms
- **Children upsert**: p95 < 200ms
- **CSV export**: p95 < 2s (streaming)
- **Health checks**: p95 < 50ms
- **Dictionary lookups**: p95 < 100ms

### Memory Usage

- **Peak memory**: < 512MB for typical workloads
- **Database connections**: Pooled, max 10 concurrent
- **CSV export**: Streaming response, no memory accumulation

## Database Optimization

### Required Indexes

The following indexes are required for optimal performance:

```sql
-- Primary performance indexes
CREATE INDEX IF NOT EXISTS idx_nodes_parent_slot ON nodes(parent_id, slot);
CREATE INDEX IF NOT EXISTS idx_nodes_label_depth ON nodes(label, depth);
CREATE INDEX IF NOT EXISTS idx_nodes_parent_label ON nodes(parent_id, label);

-- Additional indexes for specific queries
CREATE INDEX IF NOT EXISTS idx_nodes_depth ON nodes(depth);
CREATE INDEX IF NOT EXISTS idx_nodes_updated_at ON nodes(updated_at);
```

### Query Optimization

1. **Use EXPLAIN QUERY PLAN** to verify index usage
2. **Avoid full table scans** for large datasets
3. **Use parameterized queries** to prevent SQL injection
4. **Limit result sets** with appropriate WHERE clauses

### Example Optimized Queries

```sql
-- Parents with incomplete children (uses idx_nodes_parent_slot)
SELECT n.id, n.label, n.depth, n.updated_at,
       COUNT(c.id) as child_count
FROM nodes n
LEFT JOIN nodes c ON c.parent_id = n.id
WHERE n.depth = 0 OR (n.depth > 0 AND n.parent_id IS NOT NULL)
GROUP BY n.id, n.label, n.depth, n.updated_at
HAVING child_count < 5
ORDER BY n.depth, n.id;

-- Conflict detection (uses idx_nodes_parent_slot)
SELECT n1.id, n1.label, n1.slot, n2.id as conflict_id
FROM nodes n1
JOIN nodes n2 ON n1.parent_id = n2.parent_id AND n1.slot = n2.slot AND n1.id != n2.id
WHERE n1.parent_id = ?;
```

## Streaming Responses

### CSV Export

The CSV export endpoint uses streaming to handle large datasets efficiently:

```python
from fastapi.responses import StreamingResponse
import io

def generate_csv():
    """Generator function for streaming CSV data."""
    yield "Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions\n"
    
    # Stream data in chunks
    for chunk in get_data_chunks():
        yield chunk

@app.get("/api/v1/tree/export")
def export_tree():
    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=lorien_export.csv"}
    )
```

### Memory Management

1. **Use generators** for large data processing
2. **Stream responses** instead of buffering
3. **Close database connections** promptly
4. **Monitor memory usage** in production

## Caching Strategy

### Navigate Cache

The navigate endpoint uses an in-memory LRU cache:

```python
from functools import lru_cache
import time

# Cache configuration
NAVIGATE_CACHE_TTL = 60  # seconds
NAVIGATE_CACHE_SIZE = 1024  # max entries

@lru_cache(maxsize=NAVIGATE_CACHE_SIZE)
def get_cached_navigate_result(cache_key: str, timestamp: int):
    """Cached navigate result with TTL."""
    if time.time() - timestamp > NAVIGATE_CACHE_TTL:
        return None
    return compute_navigate_result(cache_key)
```

### Cache Invalidation

- **Time-based**: TTL expiration
- **Event-based**: Invalidate on data changes
- **Manual**: Clear cache on demand

## Performance Monitoring

### Metrics to Track

1. **Response times** by endpoint
2. **Database query performance**
3. **Memory usage** trends
4. **Cache hit rates**
5. **Error rates** and types

### Monitoring Tools

- **Application metrics**: Built-in FastAPI metrics
- **Database monitoring**: SQLite performance analysis
- **System metrics**: CPU, memory, disk usage
- **Log analysis**: Structured logging for performance events

### Performance Testing

Run performance tests regularly:

```bash
# Run performance test suite
pytest tests/perf/ -v

# Run with performance profiling
pytest tests/perf/ --profile

# Run specific performance tests
pytest tests/perf/test_performance_guardrails.py::test_index_usage_parents_incomplete -v
```

## Optimization Guidelines

### Code Optimization

1. **Use async/await** for I/O operations
2. **Minimize database round trips**
3. **Use connection pooling**
4. **Implement proper error handling**
5. **Profile before optimizing**

### Database Optimization

1. **Create appropriate indexes**
2. **Use prepared statements**
3. **Optimize query patterns**
4. **Monitor query performance**
5. **Regular VACUUM operations**

### API Optimization

1. **Implement pagination** for large datasets
2. **Use compression** for large responses
3. **Cache frequently accessed data**
4. **Optimize serialization**
5. **Minimize response payload size**

## Troubleshooting Performance Issues

### Common Issues

1. **Slow queries**: Check index usage with EXPLAIN
2. **Memory leaks**: Monitor memory usage over time
3. **High CPU usage**: Profile application code
4. **Slow responses**: Check network and database performance
5. **Cache misses**: Review cache configuration

### Debugging Tools

1. **SQLite EXPLAIN QUERY PLAN**
2. **Python profiler** (cProfile, line_profiler)
3. **Memory profiler** (memory_profiler)
4. **Application logs** with performance metrics
5. **Database query logs**

### Performance Regression Testing

1. **Baseline measurements** for key operations
2. **Automated performance tests** in CI/CD
3. **Performance budgets** for new features
4. **Regular performance reviews**
5. **Load testing** for production scenarios

## Best Practices

### Development

1. **Write performance tests** for new features
2. **Profile code** before optimization
3. **Use appropriate data structures**
4. **Minimize external dependencies**
5. **Follow coding standards**

### Production

1. **Monitor performance metrics**
2. **Set up alerts** for performance degradation
3. **Regular performance reviews**
4. **Capacity planning**
5. **Documentation updates**

### Maintenance

1. **Regular database maintenance**
2. **Index optimization**
3. **Cache tuning**
4. **Performance testing**
5. **Documentation updates**
