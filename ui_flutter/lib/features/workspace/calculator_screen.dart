import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import '../../core/api_config.dart';

class CalculatorScreen extends StatefulWidget {
  final String baseUrl;
  final http.Client? client;
  const CalculatorScreen(
      {super.key, this.baseUrl = ApiConfig.baseUrl, this.client});
  @override
  State<CalculatorScreen> createState() => _CalculatorScreenState();
}

class _CalculatorScreenState extends State<CalculatorScreen>
    with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => true;
  http.Client get _http => widget.client ?? http.Client();

  // data
  List<String> _roots = [];
  String? _root;
  final Map<int, String?> _levels = {
    1: null,
    2: null,
    3: null,
    4: null,
    5: null
  };
  List<Map<String, dynamic>> _options = []; // [{slot,label}]
  Map<String, dynamic>? _outcome;
  bool _loading = false;
  String? _error;

  // search (server-side 'q' filter)
  final TextEditingController _searchCtl = TextEditingController();
  Timer? _deb;

  @override
  void initState() {
    super.initState();
    _loadRoots();
  }

  @override
  void dispose() {
    _deb?.cancel();
    _searchCtl.dispose();
    super.dispose();
  }

  Future<void> _loadRoots({String? q}) async {
    setState(() => _loading = true);
    try {
      final uri = Uri.parse('${widget.baseUrl}/api/v1/tree/root-options')
          .replace(queryParameters: {
        "limit": "200",
        "offset": "0",
        if (q != null && q.isNotEmpty) "q": q
      });
      final r = await _http.get(uri);
      if (r.statusCode == 200) {
        final b = jsonDecode(r.body) as Map<String, dynamic>;
        setState(() {
          _roots = List<String>.from(b["items"] as List);
          // Keep selected root if still present, else clear selections
          if (_root != null && !_roots.contains(_root)) {
            _root = null;
            for (var i = 1; i <= 5; i++) {
              _levels[i] = null;
            }
            _options = [];
            _outcome = null;
          }
        });
      } else {
        setState(() => _error = 'Failed to load roots: HTTP ${r.statusCode}');
      }
    } catch (e) {
      setState(() => _error = 'Failed to load roots: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  Map<String, String> _buildQuery({String? q}) {
    final qp = <String, String>{};
    qp["root"] = _root!;
    for (var i = 1; i <= 5; i++) {
      final v = _levels[i];
      if (v != null && v.isNotEmpty) {
        qp["n$i"] = v;
      } else {
        break;
      }
    }
    if (q != null && q.isNotEmpty) qp["q"] = q;
    return qp;
  }

  Future<void> _navigate({String? q}) async {
    if (_root == null) return;
    setState(() {
      _loading = true;
      _error = null;
      _outcome = null;
    });
    try {
      final uri = Uri.parse('${widget.baseUrl}/api/v1/tree/navigate')
          .replace(queryParameters: _buildQuery(q: q));
      final r = await _http.get(uri);
      if (r.statusCode == 200) {
        final b = jsonDecode(r.body) as Map<String, dynamic>;
        setState(() {
          _options = List<Map<String, dynamic>>.from(
              (b["options"] as List).map((e) => Map<String, dynamic>.from(e)));
          _outcome =
              (b["outcome"] as Map?)?.map((k, v) => MapEntry(k.toString(), v));
        });
      } else if (r.statusCode == 422) {
        setState(() => _error =
            'Invalid selection. Please pick one of the suggested options.');
        final body = jsonDecode(r.body);
        if (body is Map &&
            body["detail"] is List &&
            body["detail"].isNotEmpty) {
          final ctx = body["detail"][0]["ctx"];
          if (ctx is Map && ctx["expected"] is List) {
            setState(() => _options = List<Map<String, dynamic>>.from(
                (ctx["expected"] as List)
                    .map((e) => {"slot": null, "label": e.toString()})));
          }
        }
      } else {
        setState(() => _error = 'Navigate failed: HTTP ${r.statusCode}');
      }
    } catch (e) {
      setState(() => _error = 'Navigate error: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  void _choose(String label) {
    for (var i = 1; i <= 5; i++) {
      if (_levels[i] == null || _levels[i]!.isEmpty) {
        setState(() => _levels[i] = label);
        break;
      }
      if (i == 5) return;
    }
    _navigate(q: _searchCtl.text.trim());
  }

  void _stepBack() {
    for (var i = 5; i >= 1; i--) {
      if (_levels[i] != null && _levels[i]!.isNotEmpty) {
        setState(() => _levels[i] = null);
        break;
      }
    }
    _navigate(q: _searchCtl.text.trim());
  }

  void _reset() {
    setState(() {
      for (var i = 1; i <= 5; i++) {
        _levels[i] = null;
      }
      _searchCtl.clear();
      _options = [];
      _outcome = null;
    });
  }

  void _copyPathToClipboard() {
    final path = [
      if (_root != null) _root!,
      for (var i = 1; i <= 5; i++)
        if (_levels[i] != null && _levels[i]!.isNotEmpty) _levels[i]!
    ];
    Clipboard.setData(ClipboardData(text: path.join(" > ")));
    ScaffoldMessenger.of(context)
        .showSnackBar(const SnackBar(content: Text('Path copied')));
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Calculator'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            if (Navigator.of(context).canPop()) {
              Navigator.of(context).pop();
            } else {
              Navigator.of(context)
                  .pushNamedAndRemoveUntil('/home', (_) => false);
            }
          },
        ),
        actions: [
          IconButton(
              icon: const Icon(Icons.refresh),
              tooltip: 'Reload roots',
              onPressed: () => _loadRoots()),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ROOT PICKER
            Row(children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  isExpanded: true,
                  initialValue: _root,
                  decoration: const InputDecoration(
                      labelText: 'Vital Measurement',
                      border: OutlineInputBorder()),
                  items: _roots
                      .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                      .toList(),
                  onChanged: (v) async {
                    setState(() {
                      _root = v;
                      for (var i = 1; i <= 5; i++) {
                        _levels[i] = null;
                      }
                    });
                    await _navigate(q: _searchCtl.text.trim());
                  },
                ),
              ),
              const SizedBox(width: 8),
              SizedBox(
                width: 220,
                child: TextField(
                  controller: _searchCtl,
                  decoration: const InputDecoration(
                    labelText: 'Search next step',
                    prefixIcon: Icon(Icons.search),
                    border: OutlineInputBorder(),
                  ),
                  onChanged: (text) {
                    _deb?.cancel();
                    _deb = Timer(const Duration(milliseconds: 250),
                        () => _navigate(q: text.trim()));
                  },
                ),
              ),
            ]),

            const SizedBox(height: 10),

            // PATH BREADCRUMBS
            Wrap(spacing: 8, runSpacing: 8, children: [
              InputChip(label: Text('Root: ${_root ?? "-"}')),
              for (var i = 1; i <= 5; i++)
                InputChip(
                  label: Text('Node $i: ${_levels[i] ?? "-"}'),
                  onDeleted: (_levels[i] == null || _levels[i]!.isEmpty)
                      ? null
                      : () async {
                          setState(() {
                            for (var j = i; j <= 5; j++) {
                              _levels[j] = null; // drop tail
                            }
                          });
                          await _navigate(q: _searchCtl.text.trim());
                        },
                ),
            ]),

            const Divider(),

            if (_loading) const LinearProgressIndicator(),
            if (_error != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(_error!, style: const TextStyle(color: Colors.red)),
              ),

            // NEXT OPTIONS (buttons + dropdown)
            if (_root != null) ...[
              Row(
                children: [
                  Expanded(
                    child: Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: _options
                          .take(24)
                          .map((o) => ElevatedButton(
                                onPressed: () => _choose(o["label"].toString()),
                                child: Text(o["label"].toString()),
                              ))
                          .toList(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  SizedBox(
                    width: 260,
                    child: DropdownButtonFormField<String>(
                      isExpanded: true,
                      initialValue: null,
                      decoration: const InputDecoration(
                          labelText: 'Pick from options',
                          border: OutlineInputBorder()),
                      items: _options
                          .map((o) => DropdownMenuItem(
                              value: o["label"].toString(),
                              child: Text(o["label"].toString())))
                          .toList(),
                      onChanged: (v) {
                        if (v != null) _choose(v);
                      },
                    ),
                  ),
                ],
              ),
            ],

            const SizedBox(height: 12),

            // OUTCOME
            if (_outcome != null)
              Card(
                elevation: 0,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('${_outcome!["diagnostic_triage"] ?? ""}',
                            style:
                                const TextStyle(fontWeight: FontWeight.w600)),
                        const SizedBox(height: 6),
                        Text('${_outcome!["actions"] ?? ""}'),
                      ]),
                ),
              ),

            const Spacer(),

            // ACTION BAR
            Row(children: [
              ElevatedButton.icon(
                  onPressed: _stepBack,
                  icon: const Icon(Icons.undo),
                  label: const Text('Step Back')),
              const SizedBox(width: 8),
              ElevatedButton.icon(
                  onPressed: _reset,
                  icon: const Icon(Icons.clear_all),
                  label: const Text('Clear Path')),
              const SizedBox(width: 8),
              OutlinedButton.icon(
                  onPressed: _copyPathToClipboard,
                  icon: const Icon(Icons.copy),
                  label: const Text('Copy Path')),
            ]),
          ],
        ),
      ),
    );
  }
}
