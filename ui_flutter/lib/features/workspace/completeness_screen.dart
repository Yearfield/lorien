import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'stats_details_screen.dart';

class CompletenessScreen extends StatefulWidget {
  final String baseUrl;
  final http.Client? client;
  const CompletenessScreen({
    super.key,
    this.baseUrl = const String.fromEnvironment('API_BASE_URL',
        defaultValue: 'http://127.0.0.1:8000'),
    this.client,
  });

  @override
  State<CompletenessScreen> createState() => _CompletenessScreenState();
}

class _CompletenessScreenState extends State<CompletenessScreen>
    with AutomaticKeepAliveClientMixin<CompletenessScreen> {
  bool _loading = false;
  String? _error;
  Map<String, int> _stats = {
    "nodes": 0,
    "roots": 0,
    "leaves": 0,
    "complete_paths": 0,
    "incomplete_parents": 0
  };

  // table
  static const _pageSize = 10;
  int _offset = 0;
  List<Map<String, dynamic>> _items = [];
  int _total = 0;

  http.Client get _http => widget.client ?? http.Client();

  Future<void> _loadStats() async {
    try {
      final uri = Uri.parse('${widget.baseUrl}/api/v1/tree/stats');
      final resp = await _http.get(uri);
      if (resp.statusCode == 200) {
        final body = jsonDecode(resp.body) as Map<String, dynamic>;
        _stats = {
          "nodes": (body["nodes"] as num).toInt(),
          "roots": (body["roots"] as num).toInt(),
          "leaves": (body["leaves"] as num).toInt(),
          "complete_paths": (body["complete_paths"] as num).toInt(),
          "incomplete_parents": (body["incomplete_parents"] as num).toInt(),
        };
      } else {
        _error = 'HTTP ${resp.statusCode}';
      }
    } catch (e) {
      _error = 'Load failed: $e';
    }
  }

  Future<void> _loadMissingSlots() async {
    try {
      final uri = Uri.parse(
          '${widget.baseUrl}/api/v1/tree/missing-slots-json?limit=$_pageSize&offset=$_offset');
      final resp = await _http.get(uri);
      if (resp.statusCode == 200) {
        final body = jsonDecode(resp.body) as Map<String, dynamic>;
        _items = (body["items"] as List)
            .cast<Map>()
            .map((e) => e.map((k, v) => MapEntry(k.toString(), v)))
            .toList()
            .cast<Map<String, dynamic>>();
        _total = (body["total"] as num).toInt();
      } else {
        _error = 'HTTP ${resp.statusCode}';
      }
    } catch (e) {
      _error = 'Load failed: $e';
    }
  }

  Future<void> _refresh() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    await _loadStats();
    await _loadMissingSlots();
    setState(() {
      _loading = false;
    });
  }

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  void _prev() {
    if (_offset - _pageSize >= 0) {
      _offset -= _pageSize;
      _refresh();
    }
  }

  void _next() {
    if (_offset + _pageSize < _total) {
      _offset += _pageSize;
      _refresh();
    }
  }

  void _jumpToEdit(Map<String, dynamic> row) {
    // Minimal navigation stub; Step F will implement the editor.
    Navigator.of(context).pushNamed('/edit-tree', arguments: {
      "parent_id": row["parent_id"],
      "label": row["label"],
      "depth": row["depth"],
      "missing_slots": row["missing_slots"],
    });
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Workspace → Completeness')),
      body: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (_loading) const LinearProgressIndicator(),
            if (_error != null)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Text(_error!, style: const TextStyle(color: Colors.red)),
              ),
            Wrap(
              spacing: 16,
              runSpacing: 8,
              children: [
                InkWell(
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(
                    builder: (_) => StatsDetailsScreen(
                        baseUrl: widget.baseUrl, kind: 'roots'),
                  )),
                  child: Chip(label: Text('Roots: ${_stats["roots"]}')),
                ),
                InkWell(
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(
                    builder: (_) => StatsDetailsScreen(
                        baseUrl: widget.baseUrl, kind: 'leaves'),
                  )),
                  child: Chip(label: Text('Leaves: ${_stats["leaves"]}')),
                ),
                InkWell(
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(
                    builder: (_) => StatsDetailsScreen(
                        baseUrl: widget.baseUrl, kind: 'leaves'),
                  )),
                  child: Chip(
                      label: Text(
                          'Complete paths (depth=5): ${_stats["complete_paths"]}')),
                ),
                InkWell(
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(
                    builder: (_) => StatsDetailsScreen(
                        baseUrl: widget.baseUrl, kind: 'incomplete'),
                  )),
                  child: Chip(
                      label: Text(
                          'Incomplete parents: ${_stats["incomplete_parents"]}')),
                ),
                Chip(label: Text('Nodes: ${_stats["nodes"]}')),
              ],
            ),
            const SizedBox(height: 12),
            Expanded(
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: RepaintBoundary(
                  key: const PageStorageKey('completeness_table'),
                  child: DataTable(
                    columns: const [
                      DataColumn(label: Text('Parent ID')),
                      DataColumn(label: Text('Label')),
                      DataColumn(label: Text('Depth')),
                      DataColumn(label: Text('Missing Slots')),
                      DataColumn(label: Text('')),
                    ],
                    rows: _items.map((row) {
                      final missing = (row["missing_slots"] as List).join(", ");
                      return DataRow(cells: [
                        DataCell(Text('${row["parent_id"]}')),
                        DataCell(Text('${row["label"]}')),
                        DataCell(Text('${row["depth"]}')),
                        DataCell(Text(missing)),
                        DataCell(
                          TextButton(
                            onPressed: () => _jumpToEdit(row),
                            child: const Text('Jump to Edit'),
                          ),
                        ),
                      ]);
                    }).toList(),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                    'Rows: ${_items.length} / Total: $_total  •  Offset: $_offset'),
                Row(children: [
                  OutlinedButton(onPressed: _prev, child: const Text('Prev')),
                  const SizedBox(width: 8),
                  OutlinedButton(onPressed: _next, child: const Text('Next')),
                ]),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  bool get wantKeepAlive => true;
}
