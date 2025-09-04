import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/dictionary_repository.dart';

class DictionaryScreen extends ConsumerStatefulWidget {
  const DictionaryScreen({super.key});

  @override
  ConsumerState<DictionaryScreen> createState() => _DictionaryScreenState();
}

class _DictionaryScreenState extends ConsumerState<DictionaryScreen> {
  String? _type = "vital_measurement";
  String _query = "";
  int _offset = 0;
  DictionaryPage? _page;
  final _termCtrl = TextEditingController();
  final _hintsCtrl = TextEditingController();
  String _normPreview = "";
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final repo = ref.read(dictionaryRepositoryProvider);
    setState(() => _loading = true);
    try {
      final p = await repo.list(type: _type, query: _query, limit: 50, offset: _offset);
      if (mounted) setState(() => _page = p);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to load dictionary: $e')));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _previewNormalize() async {
    if (_termCtrl.text.isEmpty) {
      setState(() => _normPreview = "");
      return;
    }
    final repo = ref.read(dictionaryRepositoryProvider);
    try {
      final n = await repo.normalize(_type!, _termCtrl.text);
      if (mounted) setState(() => _normPreview = n);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to normalize: $e')));
      }
    }
  }

  Future<void> _create() async {
    if (_termCtrl.text.isEmpty) return;
    final repo = ref.read(dictionaryRepositoryProvider);
    setState(() => _loading = true);
    try {
      await repo.create(
        type: _type!,
        term: _termCtrl.text,
        normalized: _normPreview.isEmpty ? null : _normPreview,
        hints: _hintsCtrl.text.isEmpty ? null : _hintsCtrl.text,
      );
      _termCtrl.clear();
      _hintsCtrl.clear();
      _normPreview = "";
      await _load();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Term added successfully')));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Create failed: $e')));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _edit(DictionaryEntry it) async {
    final term = TextEditingController(text: it.term);
    final hints = TextEditingController(text: it.hints ?? "");
    String norm = it.normalized;

    await showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Edit term'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: term,
              decoration: const InputDecoration(labelText: 'Term'),
              onChanged: (_) => norm = "",
            ),
            TextField(
              controller: hints,
              decoration: const InputDecoration(labelText: 'Hints (optional)'),
            ),
            const SizedBox(height: 8),
            Text('Normalized: $norm', style: const TextStyle(fontStyle: FontStyle.italic)),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              final repo = ref.read(dictionaryRepositoryProvider);
              try {
                await repo.update(it.id,
                  term: term.text,
                  normalized: norm.isEmpty ? null : norm,
                  hints: hints.text.isEmpty ? null : hints.text,
                );
                await _load();
                if (context.mounted) {
                  Navigator.of(context).pop();
                  ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Term updated successfully')));
                }
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Update failed: $e')));
                }
              }
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Dictionary')),
      body: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(children: [
          Row(children: [
            Expanded(
              child: DropdownButtonFormField<String>(
                value: _type,
                decoration: const InputDecoration(labelText: 'Type'),
                items: const [
                  DropdownMenuItem(value: "vital_measurement", child: Text('Vital Measurement')),
                  DropdownMenuItem(value: "node_label", child: Text('Node Label')),
                  DropdownMenuItem(value: "outcome_template", child: Text('Outcome Template')),
                ],
                onChanged: (v) {
                  setState(() => _type = v);
                  _load();
                }
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: TextField(
                decoration: const InputDecoration(labelText: 'Search'),
                onChanged: (v) {
                  _query = v;
                  _load();
                }
              ),
            ),
          ]),
          const Divider(),
          Row(children: [
            Expanded(
              child: TextField(
                controller: _termCtrl,
                decoration: const InputDecoration(labelText: 'Term'),
                onChanged: (_) => _previewNormalize()
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text('Normalized: $_normPreview', maxLines: 2)
            ),
            const SizedBox(width: 8),
            Expanded(
              child: TextField(
                controller: _hintsCtrl,
                decoration: const InputDecoration(labelText: 'Hints (optional)')
              )
            ),
            const SizedBox(width: 8),
            ElevatedButton(
              onPressed: _loading ? null : _create,
              child: const Text('Add')
            ),
          ]),
          const Divider(),
          Expanded(
            child: _loading
              ? const Center(child: CircularProgressIndicator())
              : _page == null
                ? const Center(child: Text('No data'))
                : ListView.separated(
                    itemBuilder: (_, i) {
                      final it = _page!.items[i];
                      return ListTile(
                        title: Text(it.term),
                        subtitle: Text('${it.type} · ${it.normalized}'),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: const Icon(Icons.edit),
                              onPressed: () => _edit(it)
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete),
                              onPressed: () async {
                                final repo = ref.read(dictionaryRepositoryProvider);
                                try {
                                  await repo.delete(it.id);
                                  await _load();
                                } catch (e) {
                                  if (mounted) {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                        SnackBar(content: Text('Delete failed: $e')));
                                  }
                                }
                              }
                            ),
                          ],
                        ),
                      );
                    },
                    separatorBuilder: (_, __) => const Divider(height: 1),
                    itemCount: _page!.items.length
                  )
          )
        ]),
      ),
    );
  }
}
