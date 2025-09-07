import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../widgets/layout/scroll_scaffold.dart';
import '../../../widgets/app_back_leading.dart';
import '../data/dictionary_repository.dart';
import '../../../providers/lorien_api_provider.dart';

class DictionaryScreen extends ConsumerStatefulWidget {
  const DictionaryScreen({super.key});

  @override
  ConsumerState<DictionaryScreen> createState() => _DictionaryScreenState();
}

class _DictionaryScreenState extends ConsumerState<DictionaryScreen> {
  String? _type;
  String _query = "";
  bool _onlyRedFlags = false;
  int _offset = 0;
  final int _limit = 50;
  DictionaryPage? _page;
  final _termCtrl = TextEditingController();
  final _hintsCtrl = TextEditingController();
  String _normPreview = "";
  bool _loading = false;
  bool _isRedFlag = false;
  bool _showNormalizedPreview = true;

  // Sorting
  String _sortBy = "label";
  bool _sortAscending = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final repo = ref.read(dictionaryRepositoryProvider);
    setState(() => _loading = true);
    try {
      final p = await repo.list(
        type: _type,
        query: _query,
        limit: _limit,
        offset: _offset,
        onlyRedFlags: _onlyRedFlags,
        sort: _sortBy,
        direction: _sortAscending ? "asc" : "desc",
      );
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

  Future<void> _loadNextPage() async {
    if (_loading || _page == null || _offset + _limit >= _page!.total) return;

    setState(() => _loading = true);
    try {
      final repo = ref.read(dictionaryRepositoryProvider);
      final nextOffset = _offset + _limit;
      final p = await repo.list(
        type: _type,
        query: _query,
        limit: _limit,
        offset: nextOffset,
        onlyRedFlags: _onlyRedFlags,
        sort: _sortBy,
        direction: _sortAscending ? "asc" : "desc",
      );

      if (mounted) {
        setState(() {
          _page = _page!.copyWith(items: [..._page!.items, ...p.items]);
          _offset = nextOffset;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to load more: $e')));
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
        isRedFlag: _isRedFlag,
      );
      _termCtrl.clear();
      _hintsCtrl.clear();
      _normPreview = "";
      _isRedFlag = false;
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

  Future<void> _exportCsv() async {
    try {
      final repo = ref.read(dictionaryRepositoryProvider);
      await repo.exportCsv(
        type: _type,
        query: _query,
        onlyRedFlags: _onlyRedFlags,
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('CSV exported successfully')));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Export failed: $e')));
      }
    }
  }

  void _toggleSort(String field) {
    if (_sortBy == field) {
      setState(() => _sortAscending = !_sortAscending);
    } else {
      setState(() {
        _sortBy = field;
        _sortAscending = true;
      });
    }
    _load();
  }

  Future<void> _edit(DictionaryEntry it) async {
    final term = TextEditingController(text: it.term);
    final hints = TextEditingController(text: it.hints ?? "");
    String norm = it.normalized;
    bool isRedFlag = it.isRedFlag ?? false;

    await showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Edit term'),
        content: SingleChildScrollView(
          child: Column(
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
                maxLines: 2,
              ),
              const SizedBox(height: 8),
              if (_showNormalizedPreview)
                Text('Normalized: $norm', style: const TextStyle(fontStyle: FontStyle.italic)),
              const SizedBox(height: 8),
              SwitchListTile(
                title: const Text('Red Flag'),
                subtitle: const Text('Mark as potentially problematic'),
                value: isRedFlag,
                onChanged: (value) => setState(() => isRedFlag = value),
              ),
            ],
          ),
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
                  isRedFlag: isRedFlag,
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
    return ScrollScaffold(
      title: 'Dictionary Management',
      leading: const AppBackLeading(),
      actions: [
        IconButton(
          icon: const Icon(Icons.download),
          onPressed: _exportCsv,
          tooltip: 'Export CSV',
        ),
        IconButton(
          icon: const Icon(Icons.sync),
          onPressed: () async {
            try {
              final api = ref.read(lorienApiProvider);
              await api.client.postJson('admin/sync-dictionary-from-tree');
              await _load();
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Dictionary refreshed from tree')),
                );
              }
            } catch (e) {
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Sync failed: $e')),
                );
              }
            }
          },
          tooltip: 'Refresh from Tree',
        ),
      ],
      children: [
        // Filters and Search
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Filters', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        value: _type,
                        decoration: const InputDecoration(labelText: 'Type'),
                        items: const [
                          DropdownMenuItem(value: null, child: Text('All Types')),
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
                    const SizedBox(width: 16),
                    Expanded(
                      child: TextField(
                        decoration: const InputDecoration(
                          labelText: 'Search terms',
                          prefixIcon: Icon(Icons.search),
                        ),
                        onChanged: (v) {
                          _query = v;
                          _load();
                        }
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Switch(
                      value: _onlyRedFlags,
                      onChanged: (value) {
                        setState(() => _onlyRedFlags = value);
                        _load();
                      },
                    ),
                    const Text('Only Red Flags'),
                    const SizedBox(width: 16),
                    Switch(
                      value: _showNormalizedPreview,
                      onChanged: (value) => setState(() => _showNormalizedPreview = value),
                    ),
                    const Text('Show Normalized Preview'),
                  ],
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Add New Term
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Add New Term', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      flex: 2,
                      child: TextField(
                        controller: _termCtrl,
                        decoration: const InputDecoration(labelText: 'Term'),
                        onChanged: (_) => _previewNormalize(),
                      ),
                    ),
                    const SizedBox(width: 16),
                    if (_showNormalizedPreview)
                      Expanded(
                        flex: 2,
                        child: Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.grey[100],
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            'Normalized: $_normPreview',
                            style: const TextStyle(fontStyle: FontStyle.italic),
                          ),
                        ),
                      ),
                    const SizedBox(width: 16),
                    Expanded(
                      flex: 2,
                      child: TextField(
                        controller: _hintsCtrl,
                        decoration: const InputDecoration(labelText: 'Hints (optional)'),
                        maxLines: 2,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Column(
                      children: [
                        const Text('Red Flag'),
                        Switch(
                          value: _isRedFlag,
                          onChanged: (value) => setState(() => _isRedFlag = value),
                        ),
                      ],
                    ),
                    const SizedBox(width: 16),
                    ElevatedButton.icon(
                      onPressed: _loading ? null : _create,
                      icon: const Icon(Icons.add),
                      label: const Text('Add Term'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Results Header
        if (_page != null)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Text(
                    '${_page!.total} terms found',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const Spacer(),
                  TextButton.icon(
                    onPressed: _load,
                    icon: const Icon(Icons.refresh),
                    label: const Text('Refresh'),
                  ),
                ],
              ),
            ),
          ),

        const SizedBox(height: 16),

        // Results Table
        Expanded(
          child: Card(
            child: _loading && _page == null
              ? const Center(child: CircularProgressIndicator())
              : _page == null || _page!.items.isEmpty
                ? const Center(child: Text('No terms found'))
                : NotificationListener<ScrollNotification>(
                    onNotification: (notification) {
                      if (notification is ScrollEndNotification &&
                          notification.metrics.extentAfter == 0) {
                        _loadNextPage();
                      }
                      return false;
                    },
                    child: SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: DataTable(
                        sortColumnIndex: _sortBy == "label" ? 0 : _sortBy == "type" ? 1 : 3,
                        sortAscending: _sortAscending,
                        columns: [
                          DataColumn(
                            label: const Text('Term'),
                            onSort: (_, __) => _toggleSort("label"),
                          ),
                          DataColumn(
                            label: const Text('Type'),
                            onSort: (_, __) => _toggleSort("type"),
                          ),
                          DataColumn(
                            label: const Text('Normalized'),
                            onSort: (_, __) => _toggleSort("normalized"),
                          ),
                          DataColumn(
                            label: const Text('Red Flag'),
                          ),
                          DataColumn(
                            label: const Text('Hints'),
                          ),
                          DataColumn(
                            label: const Text('Actions'),
                          ),
                        ],
                        rows: _page!.items.map((item) {
                          return DataRow(
                            cells: [
                              DataCell(Text(item.term)),
                              DataCell(Text(item.type.replaceAll('_', ' ').toUpperCase())),
                              DataCell(Text(item.normalized)),
                              DataCell(
                                item.isRedFlag == true
                                  ? const Icon(Icons.flag, color: Colors.red)
                                  : const Icon(Icons.flag_outlined, color: Colors.grey),
                              ),
                              DataCell(
                                Text(
                                  item.hints ?? '',
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              DataCell(
                                Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    IconButton(
                                      icon: const Icon(Icons.edit),
                                      onPressed: () => _edit(item),
                                      tooltip: 'Edit',
                                    ),
                                    IconButton(
                                      icon: const Icon(Icons.delete),
                                      onPressed: () async {
                                        final confirmed = await showDialog<bool>(
                                          context: context,
                                          builder: (context) => AlertDialog(
                                            title: const Text('Delete Term'),
                                            content: Text('Delete "${item.term}"? This action cannot be undone.'),
                                            actions: [
                                              TextButton(
                                                onPressed: () => Navigator.of(context).pop(false),
                                                child: const Text('Cancel'),
                                              ),
                                              TextButton(
                                                onPressed: () => Navigator.of(context).pop(true),
                                                style: TextButton.styleFrom(
                                                  foregroundColor: Theme.of(context).colorScheme.error,
                                                ),
                                                child: const Text('Delete'),
                                              ),
                                            ],
                                          ),
                                        );

                                        if (confirmed == true) {
                                          final repo = ref.read(dictionaryRepositoryProvider);
                                          try {
                                            await repo.delete(item.id);
                                            await _load();
                                          } catch (e) {
                                            if (mounted) {
                                              ScaffoldMessenger.of(context).showSnackBar(
                                                SnackBar(content: Text('Delete failed: $e')),
                                              );
                                            }
                                          }
                                        }
                                      },
                                      tooltip: 'Delete',
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          );
                        }).toList(),
                      ),
                    ),
                  ),
          ),
        ),

        // Loading indicator for pagination
        if (_loading && _page != null)
          const Padding(
            padding: EdgeInsets.all(16),
            child: Center(child: CircularProgressIndicator()),
          ),
      ],
    );
  }
}
