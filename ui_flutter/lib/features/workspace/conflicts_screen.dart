import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:go_router/go_router.dart';

class ConflictsScreen extends StatefulWidget {
  final String baseUrl;
  final http.Client? client;
  const ConflictsScreen({
    super.key,
    this.baseUrl = const String.fromEnvironment('API_BASE_URL', defaultValue: 'http://127.0.0.1:8000'),
    this.client,
  });
  @override
  State<ConflictsScreen> createState() => _ConflictsScreenState();
}

class _ConflictsScreenState extends State<ConflictsScreen> {
  http.Client get _http => widget.client ?? http.Client();
  bool _loading = false;
  String? _err;
  List<Map<String, dynamic>> _items = [];
  Map<String, dynamic>? _selected; // {parent_id,label,depth,...}
  List<Map<String, dynamic>> _groupChildren = []; // from conflicts/group
  final Set<String> _chosen = {};
  int? _keepId;
  final TextEditingController _newChildCtl = TextEditingController();
  final List<Map<String, dynamic>> _syntheticChildren = []; // [{label, from_id: 'new', slot: null}]

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _err = null;
    });
    try {
      final r = await _http.get(Uri.parse('${widget.baseUrl}/api/v1/tree/conflicts/conflicts?limit=50&offset=0'));
      if (r.statusCode == 200) {
        final b = jsonDecode(r.body) as Map<String, dynamic>;
        setState(() => _items = List<Map<String, dynamic>>.from((b["items"] as List).map((e) => Map<String, dynamic>.from(e))));
      } else {
        setState(() => _err = 'HTTP ${r.statusCode}');
      }
    } catch (e) {
      setState(() => _err = 'Error: $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _normalize(int parentId) async {
    setState(() => _loading = true);
    final r = await _http.post(Uri.parse('${widget.baseUrl}/api/v1/tree/conflicts/parent/$parentId/normalize'));
    setState(() => _loading = false);
    await _load();
    if (r.statusCode != 200) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Normalize failed: ${r.statusCode}')));
    }
  }

  Future<void> _loadGroupByNode(int nodeId) async {
    setState(() {
      _groupChildren = [];
      _chosen.clear();
      _keepId = null;
      _syntheticChildren.clear();
    });
    final uri = Uri.parse('${widget.baseUrl}/api/v1/tree/conflicts/group?node_id=$nodeId');
    final r = await _http.get(uri);
    if (r.statusCode == 200) {
      final b = jsonDecode(r.body) as Map<String, dynamic>;
      setState(() {
        _groupChildren = List<Map<String, dynamic>>.from((b["children"] as List).map((e) => Map<String, dynamic>.from(e)));
        final group = List<Map<String, dynamic>>.from((b["group"] as List).map((e) => Map<String, dynamic>.from(e)));
        _keepId = group.isNotEmpty ? (group.first["id"] as num).toInt() : null;
      });
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Load group failed: ${r.statusCode}')));
    }
  }

  Future<void> _confirmResolve() async {
    if (_keepId == null || _chosen.length != 5) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Choose exactly 5 children')));
      return;
    }
    final uri = Uri.parse('${widget.baseUrl}/api/v1/tree/conflicts/group/resolve');
    final r = await _http.post(uri, headers: {"Content-Type": "application/json"},
        body: jsonEncode({"keep_id": _keepId, "chosen": _chosen.toList()}));
    if (r.statusCode == 200) {
      await _load(); // refresh conflicts list
      setState(() {
        _groupChildren = [];
        _chosen.clear();
        _keepId = null;
        _selected = null;
      });
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Resolved')));
    } else {
      final body = r.body;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Resolve failed: ${r.statusCode} $body')));
    }
  }

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _newChildCtl.dispose();
    super.dispose();
  }

  void _addNewChildLabel() {
    final txt = _newChildCtl.text.trim();
    if (txt.isEmpty) return;
    if (_groupChildren.any((c) => (c["label"] ?? '') == txt) || _syntheticChildren.any((c) => (c["label"] ?? '') == txt)) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Label already present.')));
      return;
    }
    setState(() {
      _syntheticChildren.add({"child_id": null, "from_id": "new", "slot": null, "label": txt});
      // auto-select if we still have room
      if (_chosen.length < 5) _chosen.add(txt);
      _newChildCtl.clear();
    });
  }

  Future<void> _deleteSelectedParent() async {
    final pid = _selected!['parent_id'];
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Delete parent?'),
        content: const Text('This will remove the parent and its subtree. Continue?'),
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
    ) ?? false;
    
    if (!ok) return;
    
    final url = '${widget.baseUrl}/api/v1/tree/$pid';
    final r = await _http.delete(Uri.parse(url));
    if (r.statusCode == 200) {
      // remove from local list and refresh right panel
      setState(() {
        _items.removeWhere((p) => p['parent_id'] == pid);
        _selected = null;
        _groupChildren = []; // clear shown children
      });
      ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Parent deleted')));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Delete failed (${r.statusCode})')));
    }
  }

  @override
  Widget build(BuildContext context) {
    // BACK FIX: guard back to workspace if cannot pop
    Future<bool> _onWillPop() async {
      if (Navigator.of(context).canPop()) {
        return true;
      }
      // replace to workspace route if this is the root
      context.go('/workspace');
      return false;
    }

    return WillPopScope(
      onWillPop: _onWillPop,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Conflicts'),
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
              tooltip: 'Delete selected parent',
              icon: const Icon(Icons.delete_outline),
              onPressed: _selected == null ? null : _deleteSelectedParent,
            ),
          ],
        ),
        body: Row(
          children: [
            // LEFT: conflict list
            Expanded(
              flex: 1,
              child: Column(
                children: [
                  if (_loading) const LinearProgressIndicator(),
                  if (_err != null) Text(_err!, style: const TextStyle(color: Colors.red)),
                  Expanded(
                    child: ListView.builder(
                      itemCount: _items.length,
                      itemBuilder: (_, i) {
                        final it = _items[i];
                        return Card(
                          child: ListTile(
                            title: Text('${it["label"]}  (id=${it["parent_id"]})'),
                            subtitle: Text('children=${it["child_count"]} • slotDup=${it["slot_dup_count"]} • null=${it["null_slot_count"]}'),
                            onTap: () {
                              setState(() => _selected = it);
                              final nodeId = (it["parent_id"] as num?)?.toInt() ?? (it["id"] as num?)?.toInt();
                              if (nodeId != null) {
                                _loadGroupByNode(nodeId);
                              }
                            },
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
            const VerticalDivider(width: 1),
            // RIGHT: chooser
            Expanded(
              flex: 2,
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: _selected == null
                    ? const Center(child: Text('Select a conflict on the left.'))
                    : Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text('Parent ${_selected!["label"]} • id=${_selected!["parent_id"]} • Choose exactly 5 children to keep'),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              DropdownButton<int>(
                                value: _keepId,
                                hint: const Text('Keeper parent'),
                                items: _groupChildren.map((c) => c["from_id"]).toSet().map((id) => DropdownMenuItem(value: (id as num).toInt(), child: Text('Keep #$id'))).toList(),
                                onChanged: (v) => setState(() => _keepId = v),
                              ),
                              const Spacer(),
                              Text('Selected: ${_chosen.length}/5'),
                              const SizedBox(width: 8),
                              ElevatedButton.icon(
                                onPressed: _confirmResolve,
                                icon: const Icon(Icons.done_all),
                                label: const Text('Confirm'),
                              ),
                            ],
                          ),
                          const Divider(),
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
                          Expanded(
                            child: GridView.count(
                              crossAxisCount: 2,
                              childAspectRatio: 4.5,
                              children: [..._groupChildren, ..._syntheticChildren].map((c) {
                                final lbl = '${c["label"]}';
                                final selected = _chosen.contains(lbl);
                                final src = c["from_id"] == "new" ? 'new' : '${c["from_id"]}';
                                return FilterChip(
                                  label: Text('S${c["slot"] ?? "-"}: $lbl  • from $src'),
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
                          const Text('Tip: choose the best five, then Confirm. All other children under the kept parent will be removed; duplicates will be merged.'),
                        ],
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
