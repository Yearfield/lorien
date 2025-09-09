import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class MaintenanceScreen extends StatefulWidget {
  final String baseUrl;
  final http.Client? client;
  const MaintenanceScreen({
    super.key,
    this.baseUrl = const String.fromEnvironment('API_BASE_URL',
        defaultValue: 'http://127.0.0.1:8000'),
    this.client,
  });

  @override
  State<MaintenanceScreen> createState() => _MaintenanceScreenState();
}

class _MaintenanceScreenState extends State<MaintenanceScreen> {
  bool _confirm = false;
  bool _includeDictionary = false;
  bool _loading = false;
  String? _message;
  String? _error;

  Map<String, int> _stats = {
    "nodes": 0,
    "roots": 0,
    "leaves": 0,
    "complete_paths": 0,
    "incomplete_parents": 0,
    "root_nodes": 0,
    "root_labels": 0
  };

  http.Client get _http => widget.client ?? http.Client();

  Future<void> _loadStats() async {
    try {
      final resp =
          await _http.get(Uri.parse('${widget.baseUrl}/api/v1/tree/stats'));
      if (resp.statusCode == 200) {
        final m = jsonDecode(resp.body) as Map<String, dynamic>;
        setState(() {
          _stats = {
            "nodes": (m["nodes"] as num).toInt(),
            "roots": (m["roots"] as num).toInt(),
            "leaves": (m["leaves"] as num).toInt(),
            "complete_paths": (m["complete_paths"] as num).toInt(),
            "incomplete_parents": (m["incomplete_parents"] as num).toInt(),
            "root_nodes": (m["root_nodes"] as num?)?.toInt() ??
                (m["roots"] as num).toInt(),
            "root_labels": (m["root_labels"] as num?)?.toInt() ??
                (m["roots"] as num).toInt(),
          };
        });
      } else {
        setState(() {
          _error = 'Stats HTTP ${resp.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Stats failed: $e';
      });
    }
  }

  Future<void> _clear() async {
    setState(() {
      _loading = true;
      _error = null;
      _message = null;
    });
    final uri = Uri.parse(
        '${widget.baseUrl}/api/v1/admin/clear?include_dictionary=${_includeDictionary.toString()}');
    try {
      final resp = await _http.post(uri);
      if (resp.statusCode == 200) {
        final body = jsonDecode(resp.body) as Map<String, dynamic>;
        setState(() {
          _message =
              'Workspace cleared. Dictionary: ${body["dictionary_cleared"] == true ? "cleared" : "untouched"}';
          _confirm = false;
        });
      } else {
        setState(() {
          _error = 'Clear HTTP ${resp.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Clear failed: $e';
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
    await _loadStats();
  }

  Future<void> _confirmClearNodes() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Clear Workspace'),
        content: const Text(
            'This will remove all nodes and outcomes but keep the dictionary intact. Continue?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            child: const Text('Clear'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      setState(() {
        _loading = true;
        _error = null;
        _message = null;
      });
      try {
        final resp = await _http
            .post(Uri.parse('${widget.baseUrl}/api/v1/admin/clear-nodes'));
        if (resp.statusCode == 200) {
          setState(() {
            _message = 'Workspace cleared (nodes/outcomes only)';
          });
        } else {
          setState(() {
            _error = 'Clear nodes HTTP ${resp.statusCode}';
          });
        }
      } catch (e) {
        setState(() {
          _error = 'Clear nodes failed: $e';
        });
      } finally {
        setState(() {
          _loading = false;
        });
      }
      await _loadStats();
    }
  }

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Workspace → Maintenance')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (_loading) const LinearProgressIndicator(),
            if (_error != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(_error!, style: const TextStyle(color: Colors.red)),
              ),
            if (_message != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(_message!,
                    style: const TextStyle(color: Colors.green)),
              ),
            Wrap(
              spacing: 12,
              runSpacing: 8,
              children: [
                Chip(label: Text('Nodes: ${_stats["nodes"]}')),
                Chip(label: Text('Root nodes: ${_stats["root_nodes"]}')),
                Chip(label: Text('Root labels: ${_stats["root_labels"]}')),
                Chip(label: Text('Leaves: ${_stats["leaves"]}')),
                Chip(
                    label: Text(
                        'Complete (depth=5): ${_stats["complete_paths"]}')),
                Chip(
                    label: Text(
                        'Incomplete parents: ${_stats["incomplete_parents"]}')),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Checkbox(
                  value: _confirm,
                  onChanged: (v) => setState(() => _confirm = v ?? false),
                ),
                const Expanded(
                    child: Text(
                        'I understand this will erase all current data in the workspace.')),
              ],
            ),
            Row(
              children: [
                Switch(
                  value: _includeDictionary,
                  onChanged: (v) => setState(() => _includeDictionary = v),
                ),
                const Text('Also clear dictionary'),
              ],
            ),
            const SizedBox(height: 8),
            ElevatedButton.icon(
              onPressed: _confirmClearNodes,
              icon: const Icon(Icons.cleaning_services),
              label: const Text('Clear workspace (keep dictionary)'),
            ),
            const SizedBox(height: 8),
            ElevatedButton.icon(
              onPressed: _confirm && !_loading ? _clear : null,
              icon: const Icon(Icons.delete_forever),
              label: const Text('Clear Workspace'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            ),
          ],
        ),
      ),
    );
  }
}
