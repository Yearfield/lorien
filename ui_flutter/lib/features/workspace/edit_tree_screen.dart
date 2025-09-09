import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:go_router/go_router.dart';
import '../../core/widgets/keep_alive.dart' as keep_alive;

class EditTreeScreen extends StatefulWidget {
  final String baseUrl;
  final http.Client? client;
  const EditTreeScreen({
    super.key,
    this.baseUrl = const String.fromEnvironment('API_BASE_URL',
        defaultValue: 'http://127.0.0.1:8000'),
    this.client,
  });

  @override
  State<EditTreeScreen> createState() => _EditTreeScreenState();
}

class _EditTreeScreenState extends State<EditTreeScreen> {
  http.Client get _http => widget.client ?? http.Client();

  // Left list state
  final _searchCtl = TextEditingController();
  bool _incompleteOnly = true;
  int _depthFilter = -1; // -1 = all
  List<Map<String, dynamic>> _parents = [];
  int _total = 0, _limit = 20, _offset = 0;
  bool _loadingList = false;
  String? _listError;

  // Group by label mode
  bool _groupByLabel = true;
  List<Map<String, dynamic>> _labels = [];

  // Right pane state
  Map<String, dynamic>?
      _selectedParent; // {parent_id,label,depth,missing_slots}
  List<Map<String, dynamic>> _children = []; // [{id,slot,label}]
  final Map<int, TextEditingController> _slotInputs = {};
  bool _saving = false;
  String? _saveError;

  // Aggregate state for group by label
  Map<String, dynamic>?
      _aggregate; // {label, occurrences, union:[{label,freq}], by_parent:[...]}
  final Set<String> _chosen = {};
  final TextEditingController _newChildCtl = TextEditingController();
  final List<Map<String, dynamic>> _syntheticChildren = [];

  Future<void> _fetchParents({bool reset = false}) async {
    setState(() {
      _loadingList = true;
      _listError = null;
      if (reset) _offset = 0;
    });
    final q = _searchCtl.text.trim();
    final params = {
      "limit": "$_limit",
      "offset": "$_offset",
      "incomplete_only": "$_incompleteOnly",
      if (_depthFilter >= 0) "depth": "$_depthFilter",
      if (q.isNotEmpty) "q": q,
    };
    final uri = Uri.parse('${widget.baseUrl}/api/v1/tree/parents')
        .replace(queryParameters: params);
    try {
      final resp = await _http.get(uri);
      if (resp.statusCode == 200) {
        final body = jsonDecode(resp.body) as Map<String, dynamic>;
        final items = (body["items"] as List?) ?? <dynamic>[];
        setState(() {
          _parents = items
              .cast<Map>()
              .map((e) => e.map((k, v) => MapEntry(k.toString(), v)))
              .cast<Map<String, dynamic>>()
              .toList();
          _total = (body["total"] as num?)?.toInt() ?? 0;
        });
      } else if (resp.statusCode == 204) {
        setState(() {
          _parents = [];
          _total = 0;
        });
      } else {
        setState(() {
          _listError = 'List HTTP ${resp.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _listError = 'List failed: $e';
      });
    } finally {
      setState(() {
        _loadingList = false;
      });
    }
  }

  Future<void> _fetchChildren(int parentId) async {
    setState(() {
      _children = [];
      _slotInputs.clear();
      _saveError = null;
    });
    final uri = Uri.parse('${widget.baseUrl}/api/v1/tree/children/$parentId');
    try {
      final resp = await _http.get(uri);
      if (resp.statusCode == 200) {
        final body = jsonDecode(resp.body) as Map<String, dynamic>;
        final kids = (body["children"] as List?) ?? const [];
        setState(() {
          _children = kids
              .cast<Map>()
              .map((e) => e.map((k, v) => MapEntry(k.toString(), v)))
              .cast<Map<String, dynamic>>()
              .toList();
        });
      }
    } catch (_) {}
  }

  Future<void> _nextIncomplete() async {
    setState(() {
      _saveError = null;
    });
    final uri =
        Uri.parse('${widget.baseUrl}/api/v1/tree/next-incomplete-parent-json');
    try {
      final resp = await _http.get(uri);
      if (resp.statusCode == 204) {
        setState(() {
          _selectedParent = {"done": true};
          _children = [];
          _slotInputs.clear();
        });
        return;
      }
      if (resp.statusCode == 200) {
        final m = jsonDecode(resp.body) as Map<String, dynamic>;
        setState(() {
          _selectedParent = m.map((k, v) => MapEntry(k.toString(), v));
          _slotInputs.clear();
          for (final s in (m["missing_slots"] as List? ?? const [])) {
            _slotInputs[(s as num).toInt()] = TextEditingController();
          }
        });
        await _fetchChildren((m["parent_id"] as num).toInt());
      } else {
        setState(() {
          _saveError = 'Next HTTP ${resp.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _saveError = 'Next failed: $e';
      });
    }
  }

  Future<void> _saveSlots() async {
    if (_selectedParent == null || _selectedParent!["done"] == true) return;
    final pid = (_selectedParent!["parent_id"] as num).toInt();
    setState(() {
      _saving = true;
      _saveError = null;
    });
    try {
      for (final entry in _slotInputs.entries) {
        final slot = entry.key;
        final text = entry.value.text.trim();
        if (text.isEmpty) continue;
        final uri = Uri.parse('${widget.baseUrl}/api/v1/tree/$pid/slot/$slot');
        final resp = await _http.put(
          uri,
          headers: {"Content-Type": "application/json"},
          body: jsonEncode({"label": text}),
        );
        if (resp.statusCode == 409 || resp.statusCode == 422) {
          final body = jsonDecode(resp.body);
          final msg = (body["detail"] as List).isNotEmpty
              ? body["detail"][0]["msg"]
              : "Error";
          setState(() {
            _saveError = 'Slot $slot: $msg';
          });
          break;
        } else if (resp.statusCode != 200) {
          setState(() {
            _saveError = 'HTTP ${resp.statusCode} on slot $slot';
          });
          break;
        }
      }
    } catch (e) {
      setState(() {
        _saveError = 'Save failed: $e';
      });
    } finally {
      setState(() {
        _saving = false;
      });
    }
    await _nextIncomplete();
    await _fetchParents(reset: true);
  }

  // Group by label methods
  Future<void> _fetchLabels({bool reset = false}) async {
    setState(() {
      _loadingList = true;
      _listError = null;
      if (reset) _offset = 0;
    });
    final params = {
      "limit": "$_limit",
      "offset": "$_offset",
      "incomplete_only": "$_incompleteOnly",
      if (_depthFilter >= 0) "depth": "$_depthFilter",
      if (_searchCtl.text.isNotEmpty) "q": _searchCtl.text.trim(),
    };
    final uri = Uri.parse('${widget.baseUrl}/api/v1/tree/labels')
        .replace(queryParameters: params);
    final r = await _http.get(uri);
    if (r.statusCode == 200) {
      final b = jsonDecode(r.body) as Map<String, dynamic>;
      setState(() {
        _labels = List<Map<String, dynamic>>.from(
            (b["items"] as List).map((e) => Map<String, dynamic>.from(e)));
        _total = (b["total"] as num?)?.toInt() ?? _labels.length;
      });
    } else {
      setState(() => _listError = 'HTTP ${r.statusCode}');
    }
    setState(() {
      _loadingList = false;
    });
  }

  Future<void> _loadAggregateForLabel(String label) async {
    setState(() {
      _aggregate = null;
      _chosen.clear();
      _syntheticChildren.clear();
    });
    final r = await _http.get(Uri.parse(
        '${widget.baseUrl}/api/v1/tree/labels/${Uri.encodeComponent(label)}/aggregate'));
    if (r.statusCode == 200) {
      final m = jsonDecode(r.body) as Map<String, dynamic>;
      setState(() => _aggregate = m);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Aggregate failed: ${r.statusCode}')));
    }
  }

  void _addNewChildLabel() {
    final txt = _newChildCtl.text.trim();
    if (txt.isEmpty) return;
    if (_aggregate != null) {
      final union =
          List<Map<String, dynamic>>.from(_aggregate!["union"] as List);
      if (union.any((c) => (c["label"] ?? '') == txt) ||
          _syntheticChildren.any((c) => (c["label"] ?? '') == txt)) {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Label already present.')));
        return;
      }
    }
    setState(() {
      _syntheticChildren.add({"label": txt, "freq": 0});
      if (_chosen.length < 5) _chosen.add(txt);
      _newChildCtl.clear();
    });
  }

  Future<void> _applyToAllForLabel(String label) async {
    if (_chosen.length != 5) {
      ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Choose exactly 5 children')));
      return;
    }
    final r = await _http.post(
      Uri.parse(
          '${widget.baseUrl}/api/v1/tree/labels/${Uri.encodeComponent(label)}/apply-default'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"chosen": _chosen.toList()}),
    );
    if (r.statusCode == 200) {
      ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Applied to all occurrences')));
      await _fetchLabels(); // refresh counts
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Apply failed: ${r.statusCode} ${r.body}')));
    }
  }

  @override
  void initState() {
    super.initState();
    if (_groupByLabel) {
      _fetchLabels(reset: true);
    } else {
      _fetchParents(reset: true);
    }
  }

  @override
  void dispose() {
    for (final c in _slotInputs.values) {
      c.dispose();
    }
    _searchCtl.dispose();
    _newChildCtl.dispose();
    super.dispose();
  }

  Widget _buildAggregateView() {
    final label = _aggregate!["label"] as String;
    final occurrences = _aggregate!["occurrences"] as int;
    final union = List<Map<String, dynamic>>.from(_aggregate!["union"] as List);
    final combined = [...union, ..._syntheticChildren];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Label: $label • Used by $occurrences parents'),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _newChildCtl,
                decoration: const InputDecoration(
                  labelText: 'Add new child label',
                  border: OutlineInputBorder(),
                ),
                onSubmitted: (_) => _addNewChildLabel(),
              ),
            ),
            const SizedBox(width: 8),
            ElevatedButton.icon(
              onPressed: _addNewChildLabel,
              icon: const Icon(Icons.add),
              label: const Text('Add'),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text('Choose exactly 5 children (${_chosen.length}/5):'),
        const SizedBox(height: 8),
        Expanded(
          child: GridView.count(
            crossAxisCount: 2,
            childAspectRatio: 4.5,
            children: combined.map((c) {
              final lbl = '${c["label"]}';
              final freq = c["freq"] as int? ?? 0;
              final selected = _chosen.contains(lbl);
              return FilterChip(
                label: Text('$lbl (${freq}x)'),
                selected: selected,
                onSelected: (_) {
                  setState(() {
                    if (selected) {
                      _chosen.remove(lbl);
                    } else if (_chosen.length < 5) {
                      _chosen.add(lbl);
                    }
                  });
                },
              );
            }).toList(),
          ),
        ),
        const SizedBox(height: 8),
        ElevatedButton.icon(
          onPressed:
              _chosen.length == 5 ? () => _applyToAllForLabel(label) : null,
          icon: const Icon(Icons.done_all),
          label: const Text('Apply to all'),
        ),
      ],
    );
  }

  Widget _buildParentView() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Parent: ${_selectedParent!["label"]}  •  id=${_selectedParent!["parent_id"]}  •  depth=${_selectedParent!["depth"]}',
        ),
        const SizedBox(height: 8),
        const Text('Existing children:'),
        const SizedBox(height: 4),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: _children
              .map((c) => Chip(label: Text('S${c["slot"]}: ${c["label"]}')))
              .toList(),
        ),
        const SizedBox(height: 12),
        const Text('Fill missing slots (leave blank to skip):'),
        const SizedBox(height: 8),
        Expanded(
          child: ListView(
            key: const PageStorageKey('edit-slots'),
            children: _slotInputs.entries.map((e) {
              final slot = e.key;
              final ctl = e.value;
              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: TextField(
                  controller: ctl,
                  decoration: InputDecoration(
                    border: const OutlineInputBorder(),
                    labelText: 'Slot $slot label',
                  ),
                ),
              );
            }).toList(),
          ),
        ),
        if (_saveError != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(_saveError!, style: const TextStyle(color: Colors.red)),
          ),
        ElevatedButton(
          onPressed: _saving ? null : _saveSlots,
          child: const Text('Save & Next'),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return keep_alive.KeepAlive(
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Edit Tree'),
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
          actions: [
            IconButton(
              icon: const Icon(Icons.delete_forever),
              tooltip: 'Delete Parent',
              onPressed: _selectedParent == null
                  ? null
                  : () async {
                      final pid =
                          (_selectedParent!["parent_id"] as num?)?.toInt();
                      if (pid == null) return;
                      final ok = await showDialog<bool>(
                        context: context,
                        builder: (_) => AlertDialog(
                          title: const Text('Delete parent?'),
                          content: const Text(
                              'This will delete the parent and its subtree. This cannot be undone.'),
                          actions: [
                            TextButton(
                              onPressed: () => Navigator.pop(context, false),
                              child: const Text('Cancel'),
                            ),
                            ElevatedButton(
                              onPressed: () => Navigator.pop(context, true),
                              child: const Text('Delete'),
                            ),
                          ],
                        ),
                      );
                      if (ok == true) {
                        final r = await _http.delete(
                            Uri.parse('${widget.baseUrl}/api/v1/tree/$pid'));
                        if (r.statusCode == 200) {
                          setState(() => _selectedParent = null);
                          await _fetchParents(reset: true);
                          ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('Parent deleted')));
                        } else {
                          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                              content: Text('Delete failed: ${r.statusCode}')));
                        }
                      }
                    },
            ),
            IconButton(
              icon: const Icon(Icons.home),
              tooltip: 'Home',
              onPressed: () => context.go('/'),
            ),
            IconButton(
              icon: const Icon(Icons.playlist_add_check),
              tooltip: 'Next Incomplete',
              onPressed: _nextIncomplete,
            ),
          ],
        ),
        body: Row(
          children: [
            // Left pane
            SizedBox(
              width: 420,
              child: Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.all(8),
                    child: Column(
                      children: [
                        // Group by label toggle
                        Row(
                          children: [
                            FilterChip(
                              label: const Text('Group by label'),
                              selected: _groupByLabel,
                              onSelected: (v) {
                                setState(() => _groupByLabel = v);
                                if (v) {
                                  _fetchLabels(reset: true);
                                } else {
                                  _fetchParents(reset: true);
                                }
                              },
                            ),
                            const Spacer(),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            Expanded(
                              child: TextField(
                                controller: _searchCtl,
                                decoration: InputDecoration(
                                  prefixIcon: const Icon(Icons.search),
                                  hintText: _groupByLabel
                                      ? 'Search labels'
                                      : 'Search parents',
                                ),
                                onSubmitted: (_) {
                                  if (_groupByLabel) {
                                    _fetchLabels(reset: true);
                                  } else {
                                    _fetchParents(reset: true);
                                  }
                                },
                              ),
                            ),
                            const SizedBox(width: 8),
                            DropdownButton<int>(
                              value: _depthFilter,
                              onChanged: (v) {
                                setState(() => _depthFilter = v ?? -1);
                                if (_groupByLabel) {
                                  _fetchLabels(reset: true);
                                } else {
                                  _fetchParents(reset: true);
                                }
                              },
                              items: const [
                                DropdownMenuItem(value: -1, child: Text('All')),
                                DropdownMenuItem(
                                    value: 0, child: Text('Depth 0')),
                                DropdownMenuItem(
                                    value: 1, child: Text('Depth 1')),
                                DropdownMenuItem(
                                    value: 2, child: Text('Depth 2')),
                                DropdownMenuItem(
                                    value: 3, child: Text('Depth 3')),
                                DropdownMenuItem(
                                    value: 4, child: Text('Depth 4')),
                              ],
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            const SizedBox(width: 8),
                            FilterChip(
                              label: const Text('Incomplete only'),
                              selected: _incompleteOnly,
                              onSelected: (v) {
                                setState(() => _incompleteOnly = v);
                                if (_groupByLabel) {
                                  _fetchLabels(reset: true);
                                } else {
                                  _fetchParents(reset: true);
                                }
                              },
                            ),
                            const Spacer(),
                            if (_groupByLabel) ...[
                              Text(
                                  '${_labels.length} labels • covering ~${_labels.fold<int>(0, (acc, it) => acc + (it["occurrences"] as int? ?? 0))} parents'),
                            ] else ...[
                              Text('${_parents.length} / $_total'),
                            ],
                            const SizedBox(width: 8),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const Divider(height: 8),
                  if (_loadingList) const LinearProgressIndicator(),
                  if (_listError != null)
                    Padding(
                      padding: const EdgeInsets.all(8),
                      child: Text(_listError!,
                          style: const TextStyle(color: Colors.red)),
                    ),
                  Expanded(
                    child: ListView.builder(
                      key: PageStorageKey(
                          _groupByLabel ? 'edit-labels' : 'edit-parents'),
                      itemCount:
                          _groupByLabel ? _labels.length : _parents.length,
                      itemBuilder: (_, i) {
                        if (_groupByLabel) {
                          final label = _labels[i];
                          return RepaintBoundary(
                            child: ListTile(
                              title: Text('${label["label"]}'),
                              subtitle: Text(
                                'occurrences=${label["occurrences"]} • incomplete=${label["incomplete_count"]} • depth=${label["min_depth"]}-${label["max_depth"]}',
                              ),
                              onTap: () async {
                                await _loadAggregateForLabel(label["label"]);
                              },
                            ),
                          );
                        } else {
                          final p = _parents[i];
                          return RepaintBoundary(
                            child: ListTile(
                              title: Text('${p["label"]}'),
                              subtitle: Text(
                                'id=${p["parent_id"]} • depth=${p["depth"]} • missing=${(p["missing_slots"] as List).join(",")}',
                              ),
                              onTap: () async {
                                setState(() => _selectedParent =
                                    p.map((k, v) => MapEntry(k.toString(), v)));
                                await _fetchChildren(
                                    (p["parent_id"] as num).toInt());
                                _slotInputs.clear();
                                for (final s in (p["missing_slots"] as List? ??
                                    const [])) {
                                  _slotInputs[(s as num).toInt()] =
                                      TextEditingController();
                                }
                              },
                            ),
                          );
                        }
                      },
                    ),
                  ),
                ],
              ),
            ),
            const VerticalDivider(width: 1),
            // Right pane
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: _groupByLabel
                    ? (_aggregate == null
                        ? const Center(
                            child: Text(
                                'Select a label from the list to see aggregate children.'))
                        : _buildAggregateView())
                    : (_selectedParent == null
                        ? const Center(
                            child: Text(
                                'Select a parent from the list or click "Next Incomplete".'))
                        : (_selectedParent!["done"] == true
                            ? const Center(
                                child: Text('All parents appear complete. 🎉'))
                            : _buildParentView())),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
