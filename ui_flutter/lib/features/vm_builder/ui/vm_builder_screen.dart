import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
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

  @override
  Widget build(BuildContext context) {
    final s = context.watch<VmState>();
    return Scaffold(
      appBar: AppBar(title: const Text('VM Builder')),
      body: Row(
        children: [
          // Left: Roots list
          Expanded(
            flex: 1,
            child: s.loading && s.roots.isEmpty
                ? const Center(child: CircularProgressIndicator())
                : ListView.builder(
                    itemCount: s.roots.length,
                    itemBuilder: (_, i) {
                      final it = s.roots[i];
                      return ListTile(
                        title: Text(it['label'] as String),
                        onTap: () => s.selectParent(it['id'] as int, it['label'] as String, 0),
                      );
                    },
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
                        const SizedBox(height: 12),
                        Expanded(
                          child: ListView.builder(
                            itemCount: s.children.length,
                            itemBuilder: (_, i) {
                              final label = s.children[i];
                              return ListTile(
                                title: Text(label),
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
