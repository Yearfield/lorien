import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:typed_data';
import '../state/vm_provider.dart';

class VmBuilderScreen extends StatefulWidget {
  final String baseUrl;
  const VmBuilderScreen({super.key, required this.baseUrl});

  @override
  State<VmBuilderScreen> createState() => _VmBuilderScreenState();
}

class _VmBuilderScreenState extends State<VmBuilderScreen> {
  final _newChildCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    Future.microtask(() => context.read<VmState>().loadRoots());
  }

  Widget _importPanel(VmState s) {
    String mode = 'replace'; // local default; if you want stateful, lift into VmState
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Import (EngineLongBow)', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Row(
              children: [
                StatefulBuilder(builder: (context, setState) {
                  return Row(children: [
                    Radio<String>(
                      value: 'replace',
                      groupValue: mode,
                      onChanged: s.importing ? null : (v) => setState(() => mode = v!),
                    ),
                    const Text('Replace'),
                    const SizedBox(width: 12),
                    Radio<String>(
                      value: 'append',
                      groupValue: mode,
                      onChanged: s.importing ? null : (v) => setState(() => mode = v!),
                    ),
                    const Text('Append'),
                  ]);
                }),
                const Spacer(),
                ElevatedButton(
                  onPressed: s.importing ? null : () async {
                    final result = await FilePicker.platform.pickFiles(
                      allowMultiple: false,
                      type: FileType.custom,
                      allowedExtensions: ['csv', 'xlsx', 'xls'],
                      withData: true,
                    );
                    if (result == null || result.files.isEmpty) return;
                    final f = result.files.single;
                    final bytes = f.bytes ?? Uint8List(0);
                    if (bytes.isEmpty) return;
                    await s.importBytes(mode, bytes, f.name);
                  },
                  child: s.importing ? const SizedBox(
                    width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2),
                  ) : const Text('Import'),
                ),
              ],
            ),
            if (s.importStatus != null) Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(
                s.importStatus!,
                style: TextStyle(color: s.importStatus!.startsWith('Import error') ? Colors.red : Colors.black54),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final s = context.watch<VmState>();
    return Scaffold(
      appBar: AppBar(title: const Text('VM Builder')),
      body: Row(
        children: [
          // Left: Import panel + Roots list
          Expanded(
            flex: 1,
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                children: [
                  _importPanel(s),
                  Expanded(
                    child: s.loading && s.roots.isEmpty
                        ? const Center(child: CircularProgressIndicator())
                        : ListView.builder(
                            itemCount: s.roots.length,
                            itemBuilder: (_, i) {
                              final it = s.roots[i];
                              return ListTile(
                                title: Text(it['label'] as String),
                                onTap: () => s.selectParent(it['id'] as int, it['label'] as String, 0),
                                trailing: IconButton(
                                  icon: const Icon(Icons.delete),
                                  tooltip: 'Delete root',
                                  onPressed: () async {
                                    final ok = await showDialog<bool>(
                                      context: context,
                                      builder: (_) => AlertDialog(
                                        title: const Text('Delete root?'),
                                        content: Text('Delete "${it['label']}" and its entire subtree? This cannot be undone.'),
                                        actions: [
                                          TextButton(
                                            onPressed: () => Navigator.pop(context, false), 
                                            child: const Text('Cancel')
                                          ),
                                          TextButton(
                                            onPressed: () => Navigator.pop(context, true), 
                                            child: const Text('Delete')
                                          ),
                                        ],
                                      ),
                                    );
                                    if (ok == true) {
                                      await s.deleteRoot(it['id'] as int);
                                      if (context.mounted) {
                                        ScaffoldMessenger.of(context).showSnackBar(
                                          const SnackBar(content: Text('Root deleted'))
                                        );
                                      }
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
          ),
          const VerticalDivider(width: 1),
          // Right: Current parent editor
          Expanded(
            flex: 2,
            child: s.currentParentId == null
                ? const Center(child: Text('Select a root to edit children'))
                : Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Parent: ${s.currentParentLabel}', style: Theme.of(context).textTheme.titleLarge),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(
                              child: TextField(
                                controller: _newChildCtrl,
                                decoration: const InputDecoration(
                                  labelText: 'Add child label',
                                  border: OutlineInputBorder(),
                                ),
                                onSubmitted: (v) {
                                  s.addChildLabel(v);
                                  _newChildCtrl.clear();
                                },
                              ),
                            ),
                            const SizedBox(width: 8),
                            ElevatedButton(
                              onPressed: () {
                                s.addChildLabel(_newChildCtrl.text);
                                _newChildCtrl.clear();
                              },
                              child: const Text('Add'),
                            ),
                          ],
                        ),
                        // Breadcrumb navigation
                        Row(
                          children: [
                            if (s.canGoBack())
                              TextButton.icon(
                                onPressed: s.goBack,
                                icon: const Icon(Icons.arrow_back),
                                label: const Text('Back'),
                              ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Wrap(
                                spacing: 8,
                                runSpacing: 4,
                                children: s.crumbs.map((c) {
                                  final id = c['id'] as int;
                                  final label = c['label'] as String;
                                  return ActionChip(
                                    label: Text(label),
                                    onPressed: () => s.jumpToCrumb(id),
                                  );
                                }).toList(),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Expanded(
                          child: ListView.builder(
                            itemCount: s.children.length,
                            itemBuilder: (_, i) {
                              final label = s.children[i];
                              return ListTile(
                                title: Text(label),
                                onTap: () => s.drillIntoChildByIndex(i),
                                trailing: IconButton(
                                  icon: const Icon(Icons.delete),
                                  onPressed: () => s.removeChildAt(i),
                                ),
                              );
                            },
                          ),
                        ),
                        Row(
                          children: [
                            ElevatedButton(
                              onPressed: s.loading ? null : () async {
                                await s.save();
                                if (context.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(content: Text('Saved children')),
                                  );
                                }
                              },
                              child: s.loading ? const CircularProgressIndicator() : const Text('Save'),
                            ),
                          ],
                        )
                      ],
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}
