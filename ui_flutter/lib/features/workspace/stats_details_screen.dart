import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:go_router/go_router.dart';

class StatsDetailsScreen extends StatefulWidget {
  final String baseUrl;
  final String kind; // 'roots' | 'leaves' | 'incomplete'
  final http.Client? client;
  const StatsDetailsScreen({
    super.key,
    required this.kind,
    this.baseUrl = const String.fromEnvironment('API_BASE_URL', defaultValue: 'http://127.0.0.1:8000'),
    this.client,
  });
  @override
  State<StatsDetailsScreen> createState() => _StatsDetailsScreenState();
}

class _StatsDetailsScreenState extends State<StatsDetailsScreen> {
  http.Client get _http => widget.client ?? http.Client();
  List<Map<String, dynamic>> _items = [];
  bool _loading = false;
  String? _err;

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _err = null;
    });
    Uri uri;
    if (widget.kind == 'roots') {
      uri = Uri.parse('${widget.baseUrl}/api/v1/tree/roots?limit=100&offset=0');
    } else if (widget.kind == 'leaves') {
      uri = Uri.parse('${widget.baseUrl}/api/v1/tree/leaves?limit=100&offset=0');
    } else { // incomplete
      uri = Uri.parse('${widget.baseUrl}/api/v1/tree/missing-slots-json?limit=100&offset=0');
    }
    try {
      final r = await _http.get(uri);
      if (r.statusCode == 200) {
        final b = jsonDecode(r.body) as Map<String, dynamic>;
        final list = (b["items"] as List?) ?? (b["items"] ?? []);
        setState(() => _items = List<Map<String, dynamic>>.from(list.map((e) => Map<String, dynamic>.from(e))));
      } else {
        setState(() => _err = 'HTTP ${r.statusCode}');
      }
    } catch (e) {
      setState(() => _err = 'Error: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  Widget build(BuildContext context) {
    final title = widget.kind == 'roots' ? 'Roots' : widget.kind == 'leaves' ? 'Leaves' : 'Incomplete Parents';
    return Scaffold(
      appBar: AppBar(
        title: Text('Stats • $title'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            if (Navigator.of(context).canPop()) {
              Navigator.of(context).pop();
            } else {
              // Fallback to Workspace using GoRouter
              context.go('/workspace');
            }
          },
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            if (_loading) const LinearProgressIndicator(),
            if (_err != null) Text(_err!, style: const TextStyle(color: Colors.red)),
            Expanded(
              child: ListView.builder(
                itemCount: _items.length,
                itemBuilder: (_, i) {
                  final it = _items[i];
                  return ListTile(
                    title: Text(it["label"]?.toString() ?? it["parent_id"]?.toString() ?? it.toString()),
                    subtitle: Text(it.entries.map((e) => '${e.key}=${e.value}').take(6).join(' • ')),
                  );
                },
              ),
            )
          ],
        ),
      ),
    );
  }
}