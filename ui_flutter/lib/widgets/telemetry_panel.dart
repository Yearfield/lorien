"""
Telemetry panel for dev/staging environments.

This widget displays non-PHI metrics from /health/metrics endpoint
when analytics is enabled.
"""

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class TelemetryPanel extends StatefulWidget {
  final String apiBaseUrl;
  final bool enabled;

  const TelemetryPanel({
    Key? key,
    required this.apiBaseUrl,
    this.enabled = false,
  }) : super(key: key);

  @override
  State<TelemetryPanel> createState() => _TelemetryPanelState();
}

class _TelemetryPanelState extends State<TelemetryPanel> {
  Map<String, dynamic>? _metrics;
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    if (widget.enabled) {
      _loadMetrics();
    }
  }

  Future<void> _loadMetrics() async {
    if (!widget.enabled) return;

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final response = await http.get(
        Uri.parse('${widget.apiBaseUrl}/api/v1/health/metrics'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        setState(() {
          _metrics = json.decode(response.body);
          _loading = false;
        });
      } else if (response.statusCode == 404) {
        setState(() {
          _error = 'Analytics disabled';
          _loading = false;
        });
      } else {
        setState(() {
          _error = 'Failed to load metrics: ${response.statusCode}';
          _loading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error loading metrics: $e';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.enabled) {
      return const SizedBox.shrink();
    }

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
                  'Telemetry Metrics',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.refresh),
                  onPressed: _loadMetrics,
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
            else if (_metrics != null)
              _buildMetricsContent()
            else
              const Text('No metrics available'),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricsContent() {
    final telemetry = _metrics!['telemetry'] as Map<String, dynamic>? ?? {};
    final tableCounts = _metrics!['table_counts'] as Map<String, dynamic>? ?? {};

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSection('Route Hits', telemetry['route_hits']),
        _buildSection('Status Codes', telemetry['status_codes']),
        _buildSection('Table Counts', tableCounts),
        _buildUptime(telemetry['uptime_seconds']),
        _buildCounters(telemetry),
      ],
    );
  }

  Widget _buildSection(String title, dynamic data) {
    if (data == null || (data is Map && data.isEmpty)) {
      return const SizedBox.shrink();
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 4),
          if (data is Map)
            ...data.entries.map((entry) => Padding(
                  padding: const EdgeInsets.only(left: 16.0),
                  child: Text('${entry.key}: ${entry.value}'),
                ))
          else
            Text(data.toString()),
        ],
      ),
    );
  }

  Widget _buildUptime(dynamic uptimeSeconds) {
    if (uptimeSeconds == null) return const SizedBox.shrink();

    final uptime = Duration(seconds: uptimeSeconds.round());
    final hours = uptime.inHours;
    final minutes = uptime.inMinutes.remainder(60);
    final seconds = uptime.inSeconds.remainder(60);

    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Uptime',
            style: TextStyle(fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 4),
          Text('${hours}h ${minutes}m ${seconds}s'),
        ],
      ),
    );
  }

  Widget _buildCounters(Map<String, dynamic> telemetry) {
    final counters = [
      'import_success',
      'import_errors',
      'export_success',
      'export_errors',
      'conflict_count',
      'validation_errors',
    ];

    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Counters',
            style: TextStyle(fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 4),
          ...counters.map((counter) => Padding(
                padding: const EdgeInsets.only(left: 16.0),
                child: Text('$counter: ${telemetry[counter] ?? 0}'),
              )),
        ],
      ),
    );
  }
}
