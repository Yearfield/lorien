"""
Performance monitoring panel for database and cache statistics.

This widget displays performance metrics and provides optimization tools
for database indexes and cache management.
"""

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class PerformancePanel extends StatefulWidget {
  final String apiBaseUrl;

  const PerformancePanel({
    Key? key,
    required this.apiBaseUrl,
  }) : super(key: key);

  @override
  State<PerformancePanel> createState() => _PerformancePanelState();
}

class _PerformancePanelState extends State<PerformancePanel> {
  Map<String, dynamic>? _dbStats;
  Map<String, dynamic>? _cacheStats;
  Map<String, dynamic>? _healthStatus;
  bool _loading = false;
  String? _error;
  bool _creatingIndexes = false;
  bool _clearingCache = false;

  @override
  void initState() {
    super.initState();
    _loadPerformanceData();
  }

  Future<void> _loadPerformanceData() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      // Load database stats
      final dbResponse = await http.get(
        Uri.parse('${widget.apiBaseUrl}/api/v1/admin/performance/database-stats'),
        headers: {'Content-Type': 'application/json'},
      );

      if (dbResponse.statusCode == 200) {
        final dbData = json.decode(dbResponse.body);
        setState(() {
          _dbStats = dbData['database_stats'];
          _cacheStats = dbData['cache_stats'];
        });
      }

      // Load performance health
      final healthResponse = await http.get(
        Uri.parse('${widget.apiBaseUrl}/api/v1/admin/performance/health'),
        headers: {'Content-Type': 'application/json'},
      );

      if (healthResponse.statusCode == 200) {
        final healthData = json.decode(healthResponse.body);
        setState(() {
          _healthStatus = healthData;
        });
      }

      setState(() {
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Error loading performance data: $e';
        _loading = false;
      });
    }
  }

  Future<void> _createIndexes() async {
    setState(() {
      _creatingIndexes = true;
    });

    try {
      final response = await http.post(
        Uri.parse('${widget.apiBaseUrl}/api/v1/admin/performance/create-indexes'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result['message'] ?? 'Indexes created successfully'),
            backgroundColor: Colors.green,
          ),
        );
        
        // Refresh data
        _loadPerformanceData();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to create indexes: ${response.statusCode}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error creating indexes: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() {
        _creatingIndexes = false;
      });
    }
  }

  Future<void> _clearCache() async {
    setState(() {
      _clearingCache = true;
    });

    try {
      final response = await http.post(
        Uri.parse('${widget.apiBaseUrl}/api/v1/admin/performance/clear-cache'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Cache cleared successfully'),
            backgroundColor: Colors.green,
          ),
        );
        
        // Refresh data
        _loadPerformanceData();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to clear cache: ${response.statusCode}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error clearing cache: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() {
        _clearingCache = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(8.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Performance Monitor',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.refresh),
                  onPressed: _loading ? null : _loadPerformanceData,
                ),
              ],
            ),
            const SizedBox(height: 8),
            if (_loading)
              const Center(child: CircularProgressIndicator())
            else if (_error != null)
              Text(
                _error!,
                style: const TextStyle(color: Colors.red),
              )
            else if (_dbStats != null)
              _buildPerformanceContent()
            else
              const Text('No performance data available'),
          ],
        ),
      ),
    );
  }

  Widget _buildPerformanceContent() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Performance health status
        if (_healthStatus != null) _buildHealthStatus(),
        
        const SizedBox(height: 16),
        
        // Database statistics
        _buildDatabaseStats(),
        
        const SizedBox(height: 16),
        
        // Cache statistics
        if (_cacheStats != null) _buildCacheStats(),
        
        const SizedBox(height: 16),
        
        // Performance actions
        _buildPerformanceActions(),
      ],
    );
  }

  Widget _buildHealthStatus() {
    final status = _healthStatus!['performance_status'] as String? ?? 'unknown';
    final recommendations = _healthStatus!['recommendations'] as List<dynamic>? ?? [];
    
    Color statusColor;
    IconData statusIcon;
    
    switch (status) {
      case 'healthy':
        statusColor = Colors.green;
        statusIcon = Icons.check_circle;
        break;
      case 'needs_optimization':
        statusColor = Colors.orange;
        statusIcon = Icons.warning;
        break;
      case 'cache_inefficient':
        statusColor = Colors.blue;
        statusIcon = Icons.cached;
        break;
      default:
        statusColor = Colors.grey;
        statusIcon = Icons.help;
    }
    
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: statusColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: statusColor.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(statusIcon, color: statusColor, size: 20),
              const SizedBox(width: 8),
              Text(
                'Performance Status: ${status.toUpperCase()}',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: statusColor,
                ),
              ),
            ],
          ),
          if (recommendations.isNotEmpty) ...[
            const SizedBox(height: 8),
            const Text(
              'Recommendations:',
              style: TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 4),
            ...recommendations.map((rec) => Padding(
              padding: const EdgeInsets.only(left: 8, top: 2),
              child: Text(
                '• ${rec.toString()}',
                style: const TextStyle(fontSize: 12),
              ),
            )),
          ],
        ],
      ),
    );
  }

  Widget _buildDatabaseStats() {
    final totalNodes = _dbStats!['total_nodes'] as int? ?? 0;
    final rootNodes = _dbStats!['root_nodes'] as int? ?? 0;
    final leafNodes = _dbStats!['leaf_nodes'] as int? ?? 0;
    final dbSizeMb = _dbStats!['database_size_mb'] as double? ?? 0.0;
    final indexCount = (_dbStats!['indexes'] as List?)?.length ?? 0;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Database Statistics',
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 8),
        _buildStatRow('Total Nodes', totalNodes.toString()),
        _buildStatRow('Root Nodes', rootNodes.toString()),
        _buildStatRow('Leaf Nodes', leafNodes.toString()),
        _buildStatRow('Database Size', '${dbSizeMb.toStringAsFixed(2)} MB'),
        _buildStatRow('Indexes', indexCount.toString()),
      ],
    );
  }

  Widget _buildCacheStats() {
    final size = _cacheStats!['size'] as int? ?? 0;
    final maxSize = _cacheStats!['max_size'] as int? ?? 0;
    final hitRate = _cacheStats!['hit_rate_percent'] as double? ?? 0.0;
    final totalRequests = _cacheStats!['total_requests'] as int? ?? 0;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Cache Statistics',
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 8),
        _buildStatRow('Cache Size', '$size / $maxSize'),
        _buildStatRow('Hit Rate', '${hitRate.toStringAsFixed(1)}%'),
        _buildStatRow('Total Requests', totalRequests.toString()),
      ],
    );
  }

  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }

  Widget _buildPerformanceActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Performance Actions',
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            ElevatedButton.icon(
              onPressed: _creatingIndexes ? null : _createIndexes,
              icon: _creatingIndexes 
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.speed),
              label: Text(_creatingIndexes ? 'Creating...' : 'Create Indexes'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
              ),
            ),
            const SizedBox(width: 8),
            ElevatedButton.icon(
              onPressed: _clearingCache ? null : _clearCache,
              icon: _clearingCache 
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.clear_all),
              label: Text(_clearingCache ? 'Clearing...' : 'Clear Cache'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.orange,
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        const Text(
          'Create indexes for better query performance. Clear cache to reset navigation cache.',
          style: TextStyle(fontSize: 12, color: Colors.grey),
        ),
      ],
    );
  }
}

