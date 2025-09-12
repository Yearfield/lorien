"""
Audit log panel for viewing and managing audit trail.

Provides UI for viewing audit logs, performing undo operations,
and managing audit trail data.
"""

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class AuditLogPanel extends StatefulWidget {
  final String apiBaseUrl;

  const AuditLogPanel({
    Key? key,
    required this.apiBaseUrl,
  }) : super(key: key);

  @override
  State<AuditLogPanel> createState() => _AuditLogPanelState();
}

class _AuditLogPanelState extends State<AuditLogPanel> {
  List<Map<String, dynamic>> _auditEntries = [];
  bool _isLoading = false;
  String? _error;
  int _currentLimit = 50;
  int? _lastId;
  bool _hasMore = true;

  @override
  void initState() {
    super.initState();
    _loadAuditEntries();
  }

  Future<void> _loadAuditEntries({bool refresh = false}) async {
    if (refresh) {
      setState(() {
        _auditEntries.clear();
        _lastId = null;
        _hasMore = true;
      });
    }

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final url = Uri.parse('${widget.apiBaseUrl}/api/v1/admin/audit').replace(
        queryParameters: {
          'limit': _currentLimit.toString(),
          if (_lastId != null) 'after_id': _lastId.toString(),
        },
      );

      final response = await http.get(
        url,
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final newEntries = List<Map<String, dynamic>>.from(data['entries'] ?? []);
        
        setState(() {
          if (refresh) {
            _auditEntries = newEntries;
          } else {
            _auditEntries.addAll(newEntries);
          }
          _hasMore = newEntries.length == _currentLimit;
          if (newEntries.isNotEmpty) {
            _lastId = newEntries.last['id'];
          }
        });
      } else {
        setState(() {
          _error = 'Failed to load audit entries: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error loading audit entries: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _undoOperation(int auditId) async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final response = await http.post(
        Uri.parse('${widget.apiBaseUrl}/api/v1/admin/audit/$auditId/undo'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'actor': 'admin'}),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Operation undone successfully'),
            backgroundColor: Colors.green,
          ),
        );
        
        // Refresh the audit log
        _loadAuditEntries(refresh: true);
      } else {
        final errorData = json.decode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to undo: ${errorData['detail']['message'] ?? 'Unknown error'}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error undoing operation: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _showUndoConfirmation(int auditId, String operation) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Confirm Undo'),
        content: Text('Are you sure you want to undo this $operation operation?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Undo'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await _undoOperation(auditId);
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
                  'Audit Log',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.refresh),
                  onPressed: _isLoading ? null : () => _loadAuditEntries(refresh: true),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            if (_isLoading && _auditEntries.isEmpty)
              const Center(child: CircularProgressIndicator())
            else if (_error != null)
              Text(
                _error!,
                style: const TextStyle(color: Colors.red),
              )
            else if (_auditEntries.isEmpty)
              const Text('No audit entries found')
            else
              _buildAuditEntriesList(),
          ],
        ),
      ),
    );
  }

  Widget _buildAuditEntriesList() {
    return Expanded(
      child: ListView.builder(
        itemCount: _auditEntries.length + (_hasMore ? 1 : 0),
        itemBuilder: (context, index) {
          if (index == _auditEntries.length) {
            return _buildLoadMoreButton();
          }
          
          final entry = _auditEntries[index];
          return _buildAuditEntryCard(entry);
        },
      ),
    );
  }

  Widget _buildLoadMoreButton() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Center(
        child: _isLoading
            ? const CircularProgressIndicator()
            : ElevatedButton(
                onPressed: _hasMore ? () => _loadAuditEntries() : null,
                child: const Text('Load More'),
              ),
      ),
    );
  }

  Widget _buildAuditEntryCard(Map<String, dynamic> entry) {
    final isUndone = entry['undone_by'] != null;
    final isUndoable = entry['is_undoable'] == true && !isUndone;
    
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4.0),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${entry['operation']} (ID: ${entry['id']})',
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 16,
                  ),
                ),
                if (isUndone)
                  const Chip(
                    label: Text('UNDONE'),
                    backgroundColor: Colors.orange,
                    labelStyle: TextStyle(color: Colors.white, fontSize: 12),
                  )
                else if (isUndoable)
                  IconButton(
                    icon: const Icon(Icons.undo, color: Colors.blue),
                    onPressed: () => _showUndoConfirmation(
                      entry['id'],
                      entry['operation'],
                    ),
                    tooltip: 'Undo this operation',
                  ),
              ],
            ),
            const SizedBox(height: 8),
            
            Text(
              'Actor: ${entry['actor']}',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
            Text(
              'Target ID: ${entry['target_id']}',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
            Text(
              'Time: ${entry['timestamp']}',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
            
            if (entry['payload'] != null) ...[
              const SizedBox(height: 8),
              const Text(
                'Details:',
                style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12),
              ),
              Text(
                _formatPayload(entry['payload']),
                style: const TextStyle(fontSize: 11, fontFamily: 'monospace'),
              ),
            ],
            
            if (isUndone) ...[
              const SizedBox(height: 8),
              Text(
                'Undone at: ${entry['undone_at']}',
                style: const TextStyle(fontSize: 12, color: Colors.orange),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _formatPayload(Map<String, dynamic> payload) {
    // Format payload for display
    final buffer = StringBuffer();
    payload.forEach((key, value) {
      buffer.writeln('$key: $value');
    });
    return buffer.toString().trim();
  }
}

class AuditStatsPanel extends StatefulWidget {
  final String apiBaseUrl;

  const AuditStatsPanel({
    Key? key,
    required this.apiBaseUrl,
  }) : super(key: key);

  @override
  State<AuditStatsPanel> createState() => _AuditStatsPanelState();
}

class _AuditStatsPanelState extends State<AuditStatsPanel> {
  Map<String, dynamic>? _stats;
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  Future<void> _loadStats() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final response = await http.get(
        Uri.parse('${widget.apiBaseUrl}/api/v1/admin/audit/stats'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _stats = data['stats'];
        });
      } else {
        setState(() {
          _error = 'Failed to load audit stats: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error loading audit stats: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
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
                  'Audit Statistics',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.refresh),
                  onPressed: _isLoading ? null : _loadStats,
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            if (_isLoading)
              const Center(child: CircularProgressIndicator())
            else if (_error != null)
              Text(
                _error!,
                style: const TextStyle(color: Colors.red),
              )
            else if (_stats != null)
              _buildStatsContent()
            else
              const Text('No statistics available'),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsContent() {
    final stats = _stats!;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildStatRow('Total Entries', stats['total_entries'].toString()),
        _buildStatRow('Undoable Entries', stats['undoable_entries'].toString()),
        _buildStatRow('Undone Entries', stats['undone_entries'].toString()),
        
        const SizedBox(height: 16),
        const Text(
          'Operations Breakdown:',
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 8),
        
        ...(stats['operations'] as Map<String, dynamic>).entries.map(
          (entry) => _buildStatRow(entry.key, entry.value.toString()),
        ),
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
}
