"""
Data Quality panel for monitoring and repairing data quality issues.

This widget displays data quality metrics and provides repair functionality
for slot gaps and other data quality issues.
"""

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class DataQualityPanel extends StatefulWidget {
  final String apiBaseUrl;

  const DataQualityPanel({
    Key? key,
    required this.apiBaseUrl,
  }) : super(key: key);

  @override
  State<DataQualityPanel> createState() => _DataQualityPanelState();
}

class _DataQualityPanelState extends State<DataQualityPanel> {
  Map<String, dynamic>? _summary;
  bool _loading = false;
  String? _error;
  bool _repairing = false;

  @override
  void initState() {
    super.initState();
    _loadSummary();
  }

  Future<void> _loadSummary() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final response = await http.get(
        Uri.parse('${widget.apiBaseUrl}/api/v1/admin/data-quality/summary'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        setState(() {
          _summary = json.decode(response.body);
          _loading = false;
        });
      } else {
        setState(() {
          _error = 'Failed to load data quality summary: ${response.statusCode}';
          _loading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error loading data quality summary: $e';
        _loading = false;
      });
    }
  }

  Future<void> _repairSlotGaps() async {
    // Show confirmation dialog
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Repair Slot Gaps'),
        content: const Text(
          'This will fill missing child slots with "Other" placeholders. '
          'This operation is safe and can be run multiple times. Continue?'
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Repair'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    setState(() {
      _repairing = true;
    });

    try {
      final response = await http.post(
        Uri.parse('${widget.apiBaseUrl}/api/v1/admin/data-quality/repair/slot-gaps'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        
        // Show success message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result['message'] ?? 'Slot gaps repaired successfully'),
            backgroundColor: Colors.green,
          ),
        );
        
        // Refresh summary
        _loadSummary();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to repair slot gaps: ${response.statusCode}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error repairing slot gaps: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() {
        _repairing = false;
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
                  'Data Quality',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.refresh),
                  onPressed: _loading ? null : _loadSummary,
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
            else if (_summary != null)
              _buildSummaryContent()
            else
              const Text('No data quality information available'),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryContent() {
    final status = _summary!['status'] as String? ?? 'unknown';
    final slotGaps = _summary!['slot_gaps'] as int? ?? 0;
    final over5Children = _summary!['over_5_children'] as int? ?? 0;
    final orphans = _summary!['orphans'] as int? ?? 0;
    final duplicatePaths = _summary!['duplicate_paths'] as int? ?? 0;
    final totalNodes = _summary!['total_nodes'] as int? ?? 0;
    final totalParents = _summary!['total_parents'] as int? ?? 0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Status indicator
        Row(
          children: [
            Icon(
              status == 'healthy' ? Icons.check_circle : Icons.warning,
              color: status == 'healthy' ? Colors.green : Colors.orange,
              size: 20,
            ),
            const SizedBox(width: 8),
            Text(
              'Status: ${status.toUpperCase()}',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                color: status == 'healthy' ? Colors.green : Colors.orange,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        
        // Data quality metrics
        _buildMetricRow('Slot Gaps', slotGaps, Colors.orange),
        _buildMetricRow('Over 5 Children', over5Children, Colors.red),
        _buildMetricRow('Orphaned Nodes', orphans, Colors.red),
        _buildMetricRow('Duplicate Paths', duplicatePaths, Colors.orange),
        
        const SizedBox(height: 16),
        
        // Summary stats
        _buildSummaryStats(totalNodes, totalParents),
        
        const SizedBox(height: 16),
        
        // Repair actions
        if (slotGaps > 0)
          _buildRepairActions()
        else
          const Text(
            'No slot gaps detected. Data quality is good!',
            style: TextStyle(color: Colors.green),
          ),
      ],
    );
  }

  Widget _buildMetricRow(String label, int count, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: count > 0 ? color.withOpacity(0.1) : Colors.green.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              count.toString(),
              style: TextStyle(
                color: count > 0 ? color : Colors.green,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryStats(int totalNodes, int totalParents) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Database Summary',
            style: TextStyle(fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          Text('Total Nodes: $totalNodes'),
          Text('Total Parents: $totalParents'),
        ],
      ),
    );
  }

  Widget _buildRepairActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Repair Actions',
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 8),
        ElevatedButton.icon(
          onPressed: _repairing ? null : _repairSlotGaps,
          icon: _repairing 
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.build),
          label: Text(_repairing ? 'Repairing...' : 'Repair Slot Gaps'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.blue,
            foregroundColor: Colors.white,
          ),
        ),
        const SizedBox(height: 4),
        const Text(
          'This will fill missing child slots with "Other" placeholders.',
          style: TextStyle(fontSize: 12, color: Colors.grey),
        ),
      ],
    );
  }
}

