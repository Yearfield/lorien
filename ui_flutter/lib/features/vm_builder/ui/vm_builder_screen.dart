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
    Future.microtask(() {
      final state = context.read<VmState>();
      state.toast = (String message) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(message)),
          );
        }
      };
      state.loadRoots();
    });
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
                Flexible(
                  child: StatefulBuilder(builder: (context, setState) {
                    return Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Radio<String>(
                          value: 'replace',
                          groupValue: mode,
                          onChanged: s.importing ? null : (v) => setState(() => mode = v!),
                          materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        const Flexible(child: Text('Replace')),
                        const SizedBox(width: 8),
                        Radio<String>(
                          value: 'append',
                          groupValue: mode,
                          onChanged: s.importing ? null : (v) => setState(() => mode = v!),
                          materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        const Flexible(child: Text('Append')),
                      ],
                    );
                  }),
                ),
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

  Widget _rightHeader(VmState s) {
    return Row(
      children: [
        Expanded(
          child: Wrap(
            spacing: 8, 
            runSpacing: 4,
            children: s.crumbs.map((c) {
              final id = c['id'] as int;
              final label = c['label'] as String;
              return ActionChip(
                label: Text(label), 
                onPressed: () => s.jumpToCrumb(id)
              );
            }).toList(),
          ),
        ),
        const SizedBox(width: 8),
        // Export button
        FilledButton.icon(
          onPressed: s.exporting ? null : () => s.exportCurrentRoot(),
          icon: s.exporting ? const SizedBox(width:16,height:16,child:CircularProgressIndicator(strokeWidth:2)) : const Icon(Icons.download),
          label: const Text('Export'),
        ),
        const SizedBox(width: 8),
        // Next <5 button
        FilledButton.icon(
          onPressed: s.loading ? null : () async {
            final errorMessage = await s.nextUnderfilled();
            if (context.mounted) {
              if (errorMessage == null) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Jumped to next underfilled parent')),
                );
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(errorMessage)),
                );
              }
            }
          },
          icon: const Icon(Icons.filter_5),
          label: const Text('Next <5'),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final s = context.watch<VmState>();
    return Scaffold(
      appBar: AppBar(
        title: const Text('VM Builder'),
        actions: [
          IconButton(
            tooltip: 'Next Incomplete',
            onPressed: s.isBusy ? null : () => s.goToNextIncomplete(),
            icon: const Icon(Icons.fast_forward),
          ),
        ],
      ),
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
                  // + Root button
                  Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Row(
                      children: [
                        const Text('Roots', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                        const Spacer(),
                        FilledButton.icon(
                          onPressed: () async {
                            final controller = TextEditingController();
                            final result = await showDialog<String>(
                              context: context,
                              builder: (context) => AlertDialog(
                                title: const Text('Add Root'),
                                content: TextField(
                                  controller: controller,
                                  decoration: const InputDecoration(
                                    labelText: 'Root label',
                                    border: OutlineInputBorder(),
                                  ),
                                  autofocus: true,
                                ),
                                actions: [
                                  TextButton(
                                    onPressed: () => Navigator.pop(context),
                                    child: const Text('Cancel'),
                                  ),
                                  FilledButton(
                                    onPressed: () => Navigator.pop(context, controller.text.trim()),
                                    child: const Text('Add'),
                                  ),
                                ],
                              ),
                            );
                            if (result != null && result.isNotEmpty) {
                              await s.addRoot(result);
                            }
                          },
                          icon: const Icon(Icons.add),
                          label: const Text('+ Root'),
                        ),
                      ],
                    ),
                  ),
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
                                    // First select this root, then delete it
                                    await s.selectParent(it['id'] as int, it['label'] as String, 0);
                                    await s.removeCurrentRootWithConfirm(context);
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
                        Text('Parent: ${s.currentParentLabel} (${s.children.length}/5)', style: Theme.of(context).textTheme.titleLarge),
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
                        const SizedBox(height: 12),
                        // Right header with breadcrumbs and Next <5 button
                        _rightHeader(s),
                        const SizedBox(height: 12),
                        // Back button
                        if (s.canGoBack())
                          Row(
                            children: [
                              TextButton.icon(
                                onPressed: s.goBack,
                                icon: const Icon(Icons.arrow_back),
                                label: const Text('Back'),
                              ),
                            ],
                          ),
                        const SizedBox(height: 12),
                        // Red flag filter toggle
                        FilterChip(
                          label: const Text('Only red'),
                          selected: s.filterOnlyRed,
                          onSelected: (_) => s.toggleRedFilter(),
                        ),
                        const SizedBox(height: 12),
                        Expanded(
                          child: ListView.builder(
                            itemCount: s.childrenWithMeta.length,
                            itemBuilder: (_, i) {
                              final child = s.childrenWithMeta[i];
                              final label = child['label'] as String;
                              final redFlag = child['red_flag'] as bool? ?? false;
                              return ListTile(
                                title: Row(
                                  children: [
                                    if (redFlag) 
                                      Container(
                                        width: 6, 
                                        height: 6, 
                                        decoration: const BoxDecoration(
                                          color: Colors.red, 
                                          shape: BoxShape.circle
                                        ),
                                      ),
                                    if (redFlag) const SizedBox(width: 8),
                                    Expanded(child: Text(label)),
                                  ],
                                ),
                                onTap: () => s.drillIntoChildByIndex(i),
                                trailing: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    // Red flag icon
                                    IconButton(
                                      icon: Icon(redFlag ? Icons.flag : Icons.outlined_flag, 
                                               color: redFlag ? Colors.red : null),
                                      tooltip: redFlag ? 'Unflag red' : 'Mark as red flag',
                                      onPressed: () => s.toggleEdgeFlag(child['id'] as int, redFlag),
                                    ),
                                    // Clone menu
                                    PopupMenuButton<String>(
                                      onSelected: (v) { 
                                        if (v == 'clone') s.tryCloneSubtreeForChildLabel(label); 
                                      },
                                      itemBuilder: (ctx) => [ 
                                        const PopupMenuItem(value: 'clone', child: Text('Clone subtree here')) 
                                      ],
                                    ),
                                    // Delete button
                                    IconButton(
                                      icon: const Icon(Icons.delete),
                                      onPressed: () => s.removeChildAt(i),
                                    ),
                                  ],
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
