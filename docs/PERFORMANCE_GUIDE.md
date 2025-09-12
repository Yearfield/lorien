# Performance Guide

This document outlines the performance optimization features and monitoring capabilities in the Lorien decision tree application.

## Overview

The performance system provides:
- **Database Indexes**: Optimized indexes for common query patterns
- **Streaming Exports**: Memory-efficient CSV exports for large datasets
- **Navigation Caching**: In-memory cache for frequently accessed tree paths
- **Performance Monitoring**: Real-time metrics and health status

## Database Performance

### Indexes

The system automatically creates performance-optimized indexes:

- `idx_nodes_depth`: For depth-based queries
- `idx_nodes_slot`: For slot-based queries  
- `idx_nodes_parent_slot`: Composite index for efficient children queries
- `idx_nodes_leaf`: For leaf node queries (outcomes)
- `idx_nodes_label`: For label-based searches
- `idx_nodes_depth_label`: For duplicate detection
- `idx_nodes_parent_depth`: For tree structure queries

### Creating Indexes

Indexes are created automatically on first run, but can be manually created:

```bash
curl -X POST http://localhost:8000/api/v1/admin/performance/create-indexes
```

## Streaming Exports

For large datasets, use streaming exports to avoid memory issues:

### Tree Export
```bash
# Stream entire tree as CSV
curl http://localhost:8000/api/v1/admin/performance/export/tree-streaming?batch_size=1000

# Stream children for specific parent
curl http://localhost:8000/api/v1/admin/performance/export/children-streaming/123?batch_size=100
```

### Benefits
- **Memory Efficient**: Processes data in configurable batches
- **Scalable**: Works with datasets of any size
- **Fast**: Optimized for large exports

## Navigation Caching

The system includes an in-memory LRU cache for frequently accessed navigation data:

### Cache Configuration
- **Default Size**: 1000 entries
- **Eviction Policy**: Least Recently Used (LRU)
- **Scope**: Navigation and tree traversal data

### Cache Management
```bash
# Get cache statistics
curl http://localhost:8000/api/v1/admin/performance/cache-stats

# Clear cache
curl -X POST http://localhost:8000/api/v1/admin/performance/clear-cache
```

## Performance Monitoring

### Database Statistics

Get comprehensive database performance metrics:

```bash
curl http://localhost:8000/api/v1/admin/performance/database-stats
```

**Response includes:**
- Node counts by type and depth
- Database size and index information
- Performance metrics and recommendations

### Performance Health

Monitor overall system performance:

```bash
curl http://localhost:8000/api/v1/admin/performance/health
```

**Health Status Levels:**
- `healthy`: Optimal performance
- `needs_optimization`: Large dataset, consider archiving
- `cache_inefficient`: Low cache hit rate, consider tuning

### Query Analysis

Analyze specific query performance:

```bash
curl "http://localhost:8000/api/v1/admin/performance/analyze-query?query=SELECT * FROM nodes WHERE depth = 1"
```

## Performance Recommendations

The system provides automatic recommendations based on:

### Dataset Size
- **< 1,000 nodes**: No optimization needed
- **1,000 - 10,000 nodes**: Consider additional indexes
- **> 10,000 nodes**: Use streaming exports, consider data archiving

### Cache Performance
- **Hit Rate > 70%**: Optimal
- **Hit Rate 30-70%**: Consider increasing cache size
- **Hit Rate < 30%**: Review cache key strategy

### Database Size
- **< 50 MB**: No concerns
- **50-100 MB**: Monitor growth
- **> 100 MB**: Consider archiving old records

## Flutter UI Integration

### Performance Panel

The Flutter app includes a performance monitoring panel:

```dart
import 'package:lorien/widgets/performance_panel.dart';

// Add to your admin/settings screen
PerformancePanel(apiBaseUrl: 'http://localhost:8000')
```

**Features:**
- Real-time database statistics
- Cache performance metrics
- Performance health status
- One-click optimization actions

### Loading States

For long-running operations, implement loading states:

```dart
// Example for streaming export
Future<void> exportTree() async {
  setState(() => _isExporting = true);
  
  try {
    final response = await http.get(
      Uri.parse('$apiBaseUrl/api/v1/admin/performance/export/tree-streaming'),
    );
    
    // Handle streaming response
    // ...
  } finally {
    setState(() => _isExporting = false);
  }
}
```

## Best Practices

### Database Queries
1. **Use Indexes**: Ensure queries utilize available indexes
2. **Batch Operations**: Process large datasets in batches
3. **Avoid N+1 Queries**: Use JOINs or batch loading

### Caching Strategy
1. **Cache Keys**: Use consistent, meaningful cache keys
2. **Cache Invalidation**: Clear cache after data modifications
3. **Memory Management**: Monitor cache size and hit rates

### Export Operations
1. **Streaming**: Use streaming exports for large datasets
2. **Batch Size**: Tune batch size based on available memory
3. **Progress Indicators**: Show progress for long operations

## Troubleshooting

### Common Issues

**Slow Queries**
- Check if indexes are being used: `EXPLAIN QUERY PLAN`
- Consider creating additional indexes
- Review query patterns

**Memory Issues**
- Use streaming exports instead of loading all data
- Reduce batch sizes
- Monitor cache usage

**Cache Misses**
- Review cache key strategy
- Increase cache size if needed
- Check cache invalidation logic

### Performance Debugging

1. **Enable Query Logging**: Monitor slow queries
2. **Profile Memory Usage**: Identify memory bottlenecks
3. **Monitor Cache Performance**: Track hit rates and evictions

## API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/performance/database-stats` | GET | Database statistics |
| `/admin/performance/create-indexes` | POST | Create performance indexes |
| `/admin/performance/cache-stats` | GET | Cache statistics |
| `/admin/performance/clear-cache` | POST | Clear navigation cache |
| `/admin/performance/health` | GET | Performance health status |
| `/admin/performance/export/tree-streaming` | GET | Stream tree export |
| `/admin/performance/export/children-streaming/{id}` | GET | Stream children export |
| `/admin/performance/analyze-query` | GET | Analyze query performance |

### Response Formats

All endpoints return JSON with consistent structure:

```json
{
  "status": "healthy|needs_optimization|cache_inefficient",
  "database_stats": { ... },
  "cache_stats": { ... },
  "recommendations": [ ... ]
}
```

## Future Enhancements

- **Query Optimization**: Automatic query optimization suggestions
- **Predictive Caching**: ML-based cache preloading
- **Performance Alerts**: Automated performance monitoring
- **Advanced Analytics**: Detailed performance trends and patterns
