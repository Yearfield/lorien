import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class DataScreen extends StatefulWidget {
  final String baseUrl;
  final http.Client? client;
  const DataScreen({
    super.key,
    this.baseUrl = const String.fromEnvironment('API_BASE_URL',
        defaultValue: 'http://127.0.0.1:8000'),
    this.client,
  });

  @override
  State<DataScreen> createState() => _DataScreenState();
}

class _DataScreenState extends State<DataScreen>
    with AutomaticKeepAliveClientMixin<DataScreen> {
  static const _pageSize = 10;
  int _offset = 0;
  bool _loading = false;
  String? _error;
  List<Map<String, dynamic>> _rows = [];
  int _total = 0;

  http.Client get _http => widget.client ?? http.Client();

  Future<void> _fetch() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final uri = Uri.parse(
          '${widget.baseUrl}/api/v1/tree/export-json?limit=$_pageSize&offset=$_offset');
      final resp = await _http.get(uri);
      if (resp.statusCode == 200) {
        final body = jsonDecode(resp.body) as Map<String, dynamic>;
        final items = (body['items'] as List)
            .cast<Map>()
            .map((e) => e.map((k, v) => MapEntry(k.toString(), v)))
            .toList();
        setState(() {
          _rows = items.cast<Map<String, dynamic>>();
          _total = (body['total'] as num).toInt();
        });
      } else {
        setState(() {
          _error = 'HTTP ${resp.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Load failed: $e';
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    _fetch();
  }

  void _next() {
    if (_offset + _pageSize < _total) {
      _offset += _pageSize;
      _fetch();
    }
  }

  void _prev() {
    if (_offset - _pageSize >= 0) {
      _offset -= _pageSize;
      _fetch();
    }
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    const headers = [
      "Vital Measurement",
      "Node 1",
      "Node 2",
      "Node 3",
      "Node 4",
      "Node 5",
      "Diagnostic Triage",
      "Actions"
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Workspace → Data')),
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
            Expanded(
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: RepaintBoundary(
                  key: const PageStorageKey('data_screen_table'),
                  child: DataTable(
                    columns:
                        headers.map((h) => DataColumn(label: Text(h))).toList(),
                    rows: _rows.map((row) {
                      return DataRow(cells: [
                        DataCell(Text('${row["Vital Measurement"] ?? ""}')),
                        DataCell(Text('${row["Node 1"] ?? ""}')),
                        DataCell(Text('${row["Node 2"] ?? ""}')),
                        DataCell(Text('${row["Node 3"] ?? ""}')),
                        DataCell(Text('${row["Node 4"] ?? ""}')),
                        DataCell(Text('${row["Node 5"] ?? ""}')),
                        DataCell(Text('${row["Diagnostic Triage"] ?? ""}')),
                        DataCell(Text('${row["Actions"] ?? ""}')),
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
                    'Rows: ${_rows.length} / Total: $_total  •  Offset: $_offset'),
                Row(
                  children: [
                    OutlinedButton(onPressed: _prev, child: const Text('Prev')),
                    const SizedBox(width: 8),
                    OutlinedButton(onPressed: _next, child: const Text('Next')),
                  ],
                ),
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
