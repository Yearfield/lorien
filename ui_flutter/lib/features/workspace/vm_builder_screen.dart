import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:http/http.dart' as http;

class VMBuilderScreen extends StatefulWidget {
  final String baseUrl;
  final http.Client? client;
  const VMBuilderScreen(
      {super.key, this.baseUrl = 'http://127.0.0.1:8000', this.client});
  @override
  State<VMBuilderScreen> createState() => _VMBuilderScreenState();
}

class _VMBuilderScreenState extends State<VMBuilderScreen> {
  http.Client get _http => widget.client ?? http.Client();
  Map<String, dynamic>? _root; // {id,label}
  Map<String, dynamic>? _currentParent; // {id,label}
  List<Map<String, dynamic>> _children = [];
  List<Map<String, dynamic>> _suggestions = [];
  final Map<int, TextEditingController> _slotCtl = {
    for (var i = 1; i <= 5; i++) i: TextEditingController()
  };
  final TextEditingController _vmCtl = TextEditingController();
  String? _err;
  final bool _loading = false;

  @override
  void dispose() {
    for (final c in _slotCtl.values) {
      c.dispose();
    }
    _vmCtl.dispose();
    super.dispose();
  }

  Future<void> _createVM() async {
    final label = _vmCtl.text.trim();
    if (label.isEmpty) {
      setState(() => _err = 'Enter a VM label');
      return;
    }
    final r = await _http.post(Uri.parse('${widget.baseUrl}/api/v1/tree/vm'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'label': label}));
    if (r.statusCode == 200) {
      final m = jsonDecode(r.body);
      setState(() => _root = {'id': m['id'], 'label': m['label']});
      _setCurrentParent(_root!);
    } else {
      setState(() => _err = 'Create failed: ${r.statusCode} ${r.body}');
    }
  }

  Future<void> _loadChildren(int parentId) async {
    final r = await _http.get(Uri.parse(
        '${widget.baseUrl}/api/v1/tree/children?parent_id=$parentId'));
    if (r.statusCode == 200) {
      final m = jsonDecode(r.body);
      setState(() => _children = List<Map<String, dynamic>>.from(
          m['items'].map((e) => Map<String, dynamic>.from(e))));
      // prefill slot fields
      for (var i = 1; i <= 5; i++) {
        final ex =
            _children.firstWhere((e) => e['slot'] == i, orElse: () => {});
        _slotCtl[i]!.text =
            ex.isNotEmpty ? (ex['label']?.toString() ?? '') : '';
      }
    }
  }

  Future<void> _loadSuggestionsForLabel(String label) async {
    // reuse aggregate to get union under this label
    final r = await _http.get(Uri.parse(
        '${widget.baseUrl}/api/v1/tree/labels/${Uri.encodeComponent(label)}/aggregate'));
    if (r.statusCode == 200) {
      final m = jsonDecode(r.body);
      setState(
          () => _suggestions = List<Map<String, dynamic>>.from(m['union']));
    } else {
      setState(() => _suggestions = []);
    }
  }

  void _setCurrentParent(Map<String, dynamic> p) async {
    setState(() {_currentParent = p; _err = null;});
    await _loadChildren((p['id'] as num).toInt());
    await _loadSuggestionsForLabel('${p['label']}');
  }

  Future<void> _saveSlot(int slot) async {
    if (_currentParent == null) return;
    final label = _slotCtl[slot]!.text.trim();
    if (label.isEmpty) return;
    final pid = (_currentParent!['id'] as num).toInt();
    final r = await _http.put(
        Uri.parse('${widget.baseUrl}/api/v1/tree/$pid/slot/$slot'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'label': label}));
    if (r.statusCode == 200) {
      await _loadChildren(pid);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Save slot $slot failed: ${r.statusCode}')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('VM Builder'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/workspace'),
        ),
      ),
      body: Row(
        children: [
          // LEFT: create VM + child navigator
          SizedBox(
            width: 320,
            child: ListView(
              padding: const EdgeInsets.all(12),
              children: [
                const Text('Create Vital Measurement',
                    style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                TextField(
                    controller: _vmCtl,
                    decoration: const InputDecoration(
                        labelText: 'VM label', border: OutlineInputBorder())),
                const SizedBox(height: 8),
                ElevatedButton.icon(
                    onPressed: _createVM,
                    icon: const Icon(Icons.add),
                    label: const Text('Create / Use')),
                const Divider(),
                if (_root != null) ...[
                  Text('Current VM: ${_root!['label']}'),
                  const SizedBox(height: 8),
                  const Text('Navigate children:',
                      style: TextStyle(fontWeight: FontWeight.w600)),
                  ..._children.map((c) => ListTile(
                        title: Text(c['label']?.toString() ?? '(empty)'),
                        subtitle:
                            Text('slot ${c['slot']} • depth ${c['depth']}'),
                        onTap: () => _setCurrentParent(c),
                      )),
                ],
              ],
            ),
          ),
          const VerticalDivider(width: 1),
          // RIGHT: slot editor + suggestions
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: _currentParent == null
                  ? const Center(
                      child: Text('Create or select a parent on the left'))
                  : Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                          Text(
                              'Editing children of: ${_currentParent!['label']} (id=${_currentParent!['id']})'),
                          const SizedBox(height: 8),
                          Wrap(spacing: 8, runSpacing: 8, children: [
                            for (var i = 1; i <= 5; i++)
                              SizedBox(
                                width: 340,
                                child: Row(children: [
                                  Expanded(
                                      child: TextField(
                                    controller: _slotCtl[i],
                                    decoration: InputDecoration(
                                        labelText: 'Slot $i label',
                                        border: const OutlineInputBorder()),
                                    onSubmitted: (_) => _saveSlot(i),
                                  )),
                                  const SizedBox(width: 8),
                                  ElevatedButton(
                                      onPressed: () => _saveSlot(i),
                                      child: const Text('Save'))
                                ]),
                              ),
                          ]),
                          const Divider(),
                          const Text('Suggestions (from existing data):'),
                          const SizedBox(height: 8),
                          Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              children: _suggestions
                                  .map((s) => ActionChip(
                                      label:
                                          Text('${s["label"]} (${s["freq"]})'),
                                      onPressed: () {
                                        // put into the first empty slot
                                        for (var i = 1; i <= 5; i++) {
                                          if (_slotCtl[i]!
                                              .text
                                              .trim()
                                              .isEmpty) {
                                            _slotCtl[i]!.text =
                                                s["label"].toString();
                                            _saveSlot(i);
                                            break;
                                          }
                                        }
                                      }))
                                  .toList()),
                        ]),
            ),
          )
        ],
      ),
    );
  }
}
