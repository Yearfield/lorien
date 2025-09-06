import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/edit_tree_provider.dart';
import '../data/edit_tree_repository.dart';
import '../state/edit_tree_controller.dart';
import '../state/edit_tree_state.dart';
import '../../dictionary/ui/dictionary_suggestions_overlay.dart';
import '../../symptoms/data/materialization_service.dart';
import '../../../data/dto/child_slot_dto.dart';

class EditTreeScreen extends ConsumerStatefulWidget {
  const EditTreeScreen({super.key, this.parentId});

  final int? parentId; // Optional parent ID to focus on

  @override
  ConsumerState<EditTreeScreen> createState() => _EditTreeScreenState();
}

class _EditTreeScreenState extends ConsumerState<EditTreeScreen> {
  final _searchController = TextEditingController();
  int? _depth;
  int _offset = 0;
  bool _onlyIncomplete = true;
  List<IncompleteParent> _items = [];
  int _total = 0;
  int _limit = 50;
  bool _loadingList = false;

  // NEW: Persistent controllers & focus nodes by slot (1..5)
  final Map<int, TextEditingController> _controllers = {};
  final Map<int, FocusNode> _focusNodes = {};
  bool _dirty = false;
  int _tabIndex = 1; // Default to Editor tab on mobile

  // NEW: List pagination and scroll management
  final ScrollController _listScrollController = ScrollController();
  Timer? _searchDebounceTimer;
  bool _isLoadingMore = false;
  bool _hasMoreData = true;

  // NEW: Batch operations
  Set<int> _selectedParents = {};
  bool _batchMode = false;
  bool _isPerformingBatchOperation = false;

  Future<void> _loadList({bool append = false}) async {
    if (append && (_isLoadingMore || !_hasMoreData)) return;

    setState(() {
      if (append) {
        _isLoadingMore = true;
      } else {
        _loadingList = true;
      }
    });

    try {
      final repo = ref.read(editTreeRepositoryProvider);
      final currentQuery = _searchController.text.trim();
      final page = await repo.listIncomplete(
        query: currentQuery.isNotEmpty ? currentQuery : "",
        depth: _depth,
        limit: _limit,
        offset: append ? _offset + _limit : 0,
      );

      if (mounted) {
        setState(() {
          if (append) {
            _items.addAll(page.items);
            _offset += _limit;
            _isLoadingMore = false;
          } else {
            _items = page.items;
            _total = page.total;
            _offset = 0;
            _loadingList = false;
          }
          _hasMoreData = page.items.length == _limit;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _loadingList = false;
          _isLoadingMore = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load list: $e')),
        );
      }
    }
  }

  void _onSearchChanged(String query) {
    _searchDebounceTimer?.cancel();
    _searchDebounceTimer = Timer(const Duration(milliseconds: 300), () {
      setState(() {
        _offset = 0;
        _hasMoreData = true;
      });
      _loadList();
    });
  }

  Future<bool> _guardUnsavedChanges() async {
    if (!_dirty) return true;

    final result = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Unsaved Changes'),
        content: const Text(
          'You have unsaved changes. What would you like to do?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false), // Stay
            child: const Text('Stay'),
          ),
          TextButton(
            onPressed: () async {
              // Try to save and continue if successful
              try {
                await ref.read(editTreeControllerProvider.notifier).save();
                if (mounted) {
                  Navigator.of(context).pop(true); // Continue
                }
              } catch (e) {
                // Save failed, stay on current
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Failed to save: $e')),
                  );
                  Navigator.of(context).pop(false); // Stay
                }
              }
            },
            child: const Text('Save & Continue'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true), // Discard
            style: TextButton.styleFrom(
              foregroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('Discard Changes'),
          ),
        ],
      ),
    );

    return result ?? false; // Default to staying if dialog is dismissed
  }

  Future<void> _nextIncomplete() async {
    final shouldContinue = await _guardUnsavedChanges();
    if (!shouldContinue) return;

    final repo = ref.read(editTreeRepositoryProvider);
    final j = await repo.nextIncomplete();
    if (j == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('All parents complete.')),
        );
      }
      return;
    }
    await _openParent(
      j['parent_id'],
      j['label'],
      j['depth'],
      j['missing_slots'],
    );
  }

  // NEW: Batch operations
  void _toggleBatchMode() {
    setState(() {
      _batchMode = !_batchMode;
      if (!_batchMode) {
        _selectedParents.clear();
      }
    });
  }

  void _toggleParentSelection(int parentId) {
    setState(() {
      if (_selectedParents.contains(parentId)) {
        _selectedParents.remove(parentId);
      } else {
        _selectedParents.add(parentId);
      }
    });
  }

  void _selectAllParents() {
    setState(() {
      _selectedParents = Set.from(_items.map((item) => item.parentId));
    });
  }

  void _clearSelection() {
    setState(() => _selectedParents.clear());
  }

  Future<void> _batchFillWithOther() async {
    if (_selectedParents.isEmpty) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Batch Fill with "Other"'),
        content: Text(
          'This will fill empty slots in ${_selectedParents.length} selected parents with "Other". Continue?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Fill'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    setState(() => _isPerformingBatchOperation = true);

    try {
      final repo = ref.read(editTreeRepositoryProvider);
      int successCount = 0;

      for (final parentId in _selectedParents) {
        try {
          final parentData = await repo.getParentChildren(parentId);
          final children = <ChildSlotDTO>[];

          for (final child in parentData.children) {
            final label = child.label?.trim().isEmpty ?? true ? 'Other' : child.label!;
            children.add(ChildSlotDTO(slot: child.slot, label: label));
          }

          await repo.updateParentChildren(parentId, children);
          successCount++;
        } catch (e) {
          // Continue with other parents
        }
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Batch operation completed: $successCount/${_selectedParents.length} parents updated')),
        );
        _loadList();
        _clearSelection();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Batch operation failed: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isPerformingBatchOperation = false);
      }
    }
  }

  Future<void> _batchMaterialize() async {
    if (_selectedParents.isEmpty) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Batch Materialize'),
        content: Text(
          'This will materialize ${_selectedParents.length} selected parents. Continue?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Materialize'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    setState(() => _isPerformingBatchOperation = true);

    try {
      // Use the materialization service
      final service = ref.read(materializationServiceProvider);
      final parentIds = _selectedParents.toList();
      final result = await service.materializeMultipleParents(parentIds);

      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Batch Materialization Complete'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Added: ${result.added}'),
                Text('Filled: ${result.filled}'),
                Text('Pruned: ${result.pruned}'),
                Text('Kept: ${result.kept}'),
                if (result.log != null) ...[
                  const SizedBox(height: 8),
                  const Text('Log:', style: TextStyle(fontWeight: FontWeight.bold)),
                  Text(result.log!),
                ],
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('OK'),
              ),
            ],
          ),
        );
        _loadList();
        _clearSelection();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Batch materialization failed: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isPerformingBatchOperation = false);
      }
    }
  }

  Future<void> _openParent(
    int parentId,
    String label,
    int depth,
    String missing,
  ) async {
    final shouldContinue = await _guardUnsavedChanges();
    if (!shouldContinue) return;

    final c = ref.read(editTreeControllerProvider.notifier);
    await c.loadParent(parentId, label: label, depth: depth, missing: missing);
    // NEW: hydrate controllers without losing user edits if dirty
    if (!_dirty) {
      final state = ref.read(editTreeControllerProvider);
      for (var i = 1; i <= 5; i++) {
        final slotState = state.slots.firstWhere((s) => s.slot == i);
        _controllers[i]!.text = slotState.text;
        _controllers[i]!.selection =
            TextSelection.collapsed(offset: _controllers[i]!.text.length);
      }
    }
    setState(() {}); // refresh right pane
  }

  Future<void> _onNextIncompleteTap() async {
    await _nextIncomplete();
  }

  @override
  void initState() {
    super.initState();
    // Initialize persistent controllers & focus nodes
    for (var i = 1; i <= 5; i++) {
      _controllers[i] = TextEditingController();
      _focusNodes[i] = FocusNode(debugLabel: 'slot_$i');
    }
    _loadList().then((_) {
      // After loading the list, focus on the specified parent if provided
      if (widget.parentId != null) {
        _focusOnParent(widget.parentId!);
      }
    });
    _setupScrollListener();
  }

  Future<void> _focusOnParent(int parentId) async {
    // Check if the parent is already in the loaded list
    final parentInList = _items.any((item) => item.parentId == parentId);
    if (parentInList) {
      // Find the parent in the list and open it
      final parent = _items.firstWhere((item) => item.parentId == parentId);
      await _openParent(parentId, parent.label, parent.depth, parent.missingSlots);
    } else {
      // Parent not in current list, try to load it directly
      try {
        final repo = ref.read(editTreeRepositoryProvider);
        final data = await repo.nextIncomplete();
        if (data != null && data['parent_id'] == parentId) {
          await _openParent(
            data['parent_id'],
            data['label'],
            data['depth'],
            data['missing_slots'],
          );
        }
      } catch (e) {
        // If we can't find the parent, show a message
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Could not find parent with ID: $parentId')),
          );
        }
      }
    }
  }

  void _setupScrollListener() {
    _listScrollController.addListener(() {
      if (_listScrollController.position.pixels >
              _listScrollController.position.maxScrollExtent * 0.8 &&
          !_isLoadingMore &&
          _hasMoreData &&
          !_loadingList) {
        _loadMoreData();
      }
    });
  }

  Future<void> _loadMoreData() async {
    if (_isLoadingMore || !_hasMoreData) return;

    setState(() => _isLoadingMore = true);

    try {
      final repo = ref.read(editTreeRepositoryProvider);
      final currentQuery = _searchController.text.trim();
      final nextOffset = _offset + _limit;

      final page = await repo.listIncomplete(
        query: currentQuery.isNotEmpty ? currentQuery : "",
        depth: _depth,
        limit: _limit,
        offset: nextOffset,
      );

      if (mounted) {
        setState(() {
          _items.addAll(page.items);
          _offset = nextOffset;
          _hasMoreData = page.items.length == _limit;
          _isLoadingMore = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoadingMore = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load more data: $e')),
        );
      }
    }
  }

  @override
  void dispose() {
    for (final c in _controllers.values) {
      c.dispose();
    }
    for (final f in _focusNodes.values) {
      f.dispose();
    }
    _listScrollController.dispose();
    _searchDebounceTimer?.cancel();
    super.dispose();
  }

  Widget _buildListPane() {
    return Flexible(
      flex: 2,
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(8),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    decoration: const InputDecoration(
                      prefixIcon: Icon(Icons.search),
                      labelText: 'Search parents',
                    ),
                    onChanged: _onSearchChanged,
                  ),
                ),
                const SizedBox(width: 8),
                DropdownButton<int?>(
                  value: _depth,
                  hint: const Text('Depth'),
                  onChanged: (v) {
                    setState(() {
                      _depth = v;
                      _offset = 0;
                      _hasMoreData = true;
                    });
                    _loadList();
                  },
                  items: const [null, 0, 1, 2, 3, 4, 5].map((d) =>
                      DropdownMenuItem(
                        value: d,
                        child: Text(d == null ? 'All' : d.toString()),
                      ),
                  ).toList(),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Column(
              children: [
                Row(
                  children: [
                    ElevatedButton.icon(
                      onPressed: _onNextIncompleteTap,
                      icon: const Icon(Icons.skip_next),
                      label: const Text('Next Incomplete'),
                    ),
                    const SizedBox(width: 8),
                    if (_batchMode) ...[
                      ElevatedButton.icon(
                        onPressed: _selectedParents.isEmpty ? null : _batchFillWithOther,
                        icon: const Icon(Icons.edit),
                        label: const Text('Fill with Other'),
                      ),
                      const SizedBox(width: 8),
                      ElevatedButton.icon(
                        onPressed: _selectedParents.isEmpty ? null : _batchMaterialize,
                        icon: const Icon(Icons.build),
                        label: const Text('Materialize'),
                      ),
                      const SizedBox(width: 8),
                      OutlinedButton.icon(
                        onPressed: _clearSelection,
                        icon: const Icon(Icons.clear),
                        label: const Text('Clear'),
                      ),
                    ] else ...[
                      ElevatedButton.icon(
                        onPressed: _toggleBatchMode,
                        icon: const Icon(Icons.checklist),
                        label: const Text('Batch Mode'),
                      ),
                    ],
                    const Spacer(),
                    Text('$_total found'),
                  ],
                ),
                if (_batchMode) ...[
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Text('${_selectedParents.length} selected'),
                      const SizedBox(width: 16),
                      OutlinedButton(
                        onPressed: _selectAllParents,
                        child: const Text('Select All'),
                      ),
                      const SizedBox(width: 8),
                      OutlinedButton(
                        onPressed: _clearSelection,
                        child: const Text('Clear All'),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: Stack(
              children: [
                _loadingList
                    ? const Center(child: CircularProgressIndicator())
                    : ListView.separated(
                        controller: _listScrollController,
                        itemCount: _items.length + (_isLoadingMore ? 1 : 0),
                        separatorBuilder: (_, __) => const Divider(height: 1),
                        itemBuilder: (_, i) {
                          if (i == _items.length) {
                            // Loading indicator for infinite scroll
                            return const Padding(
                              padding: EdgeInsets.all(16),
                              child: Center(child: CircularProgressIndicator()),
                            );
                          }

                          final it = _items[i];
                          final isSelected = _selectedParents.contains(it.parentId);
                          return ListTile(
                            leading: _batchMode
                                ? Checkbox(
                                    value: isSelected,
                                    onChanged: (value) => _toggleParentSelection(it.parentId),
                                  )
                                : null,
                            title: Text(it.label),
                            subtitle: Text(
                              'Depth ${it.depth} • Missing: ${it.missingSlots.isEmpty ? "—" : it.missingSlots}',
                            ),
                            tileColor: isSelected ? Theme.of(context).colorScheme.primaryContainer.withOpacity(0.3) : null,
                            onTap: _batchMode
                                ? () => _toggleParentSelection(it.parentId)
                                : () => _openParent(
                                    it.parentId,
                                    it.label,
                                    it.depth,
                                    it.missingSlots,
                                  ),
                          );
                        },
                      ),
                if (_listScrollController.hasClients &&
                    _listScrollController.position.pixels > 200)
                  Positioned(
                    bottom: 16,
                    right: 16,
                    child: FloatingActionButton.small(
                      onPressed: () {
                        _listScrollController.animateTo(
                          0,
                          duration: const Duration(milliseconds: 300),
                          curve: Curves.easeInOut,
                        );
                      },
                      child: const Icon(Icons.arrow_upward),
                      tooltip: 'Scroll to top',
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEditorPane(EditTreeState st) {
    return Flexible(
      flex: 3,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: st.parentId == null
            ? const Center(
                child: Text('Select a parent from the list or click "Next Incomplete".'),
              )
            : _EditorPane(
                state: st,
                onChange: (slot, txt) =>
                    ref.read(editTreeControllerProvider.notifier).putSlot(slot, txt),
                onSave: () =>
                    ref.read(editTreeControllerProvider.notifier).save(),
                onReset: () =>
                    ref.read(editTreeControllerProvider.notifier).reset(),
                controllers: _controllers,
                focusNodes: _focusNodes,
                dirty: _dirty,
                onDirtyChanged: (dirty) => setState(() => _dirty = dirty),
              ),
      ),
    );
  }

  Widget _buildMobileLayout(EditTreeState st) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: SegmentedButton<int>(
            segments: const [
              ButtonSegment(value: 0, label: Text('List')),
              ButtonSegment(value: 1, label: Text('Editor')),
            ],
            selected: {_tabIndex},
            onSelectionChanged: (selection) {
              setState(() => _tabIndex = selection.first);
            },
          ),
        ),
        Expanded(
          child: _tabIndex == 0 ? _buildListPane() : _buildEditorPane(st),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final st = ref.watch(editTreeControllerProvider);
    return Shortcuts(
      shortcuts: <LogicalKeySet, Intent>{
        LogicalKeySet(LogicalKeyboardKey.control, LogicalKeyboardKey.keyS):
            const ActivateIntent(),
      },
      child: Actions(
        actions: <Type, Action<Intent>>{
          ActivateIntent: CallbackAction(
            onInvoke: (_) => ref.read(editTreeControllerProvider.notifier).save(),
          ),
        },
        child: FocusTraversalGroup(
          policy: OrderedTraversalPolicy(),
          child: Scaffold(
            appBar: AppBar(title: const Text('Edit Tree')),
            body: LayoutBuilder(
              builder: (context, constraints) {
                final isWide = constraints.maxWidth >= 1000;
                if (isWide) {
                  return Row(
                    children: [
                      _buildListPane(),
                      VerticalDivider(width: 1, thickness: 1, color: Theme.of(context).dividerColor),
                      _buildEditorPane(st),
                    ],
                  );
                } else {
                  return _buildMobileLayout(st);
                }
              },
            ),
            bottomNavigationBar: st.parentId == null
                ? null
                : _Footer(
                    state: st,
                    onSave: () => ref.read(editTreeControllerProvider.notifier).save(),
                    onReset: () => ref.read(editTreeControllerProvider.notifier).reset(),
                  ),
          ),
        ),
      ),
    );
  }
}

class _EditorPane extends StatefulWidget {
  final EditTreeState state;
  final void Function(int slot, String text) onChange;
  final VoidCallback onSave;
  final VoidCallback onReset;
  final Map<int, TextEditingController> controllers;
  final Map<int, FocusNode> focusNodes;
  final bool dirty;
  final void Function(bool) onDirtyChanged;

  const _EditorPane({
    required this.state,
    required this.onChange,
    required this.onSave,
    required this.onReset,
    required this.controllers,
    required this.focusNodes,
    required this.dirty,
    required this.onDirtyChanged,
    super.key,
  });

  @override
  State<_EditorPane> createState() => _EditorPaneState();
}

class _EditorPaneState extends State<_EditorPane> {

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header with breadcrumb + missing badges + Next Incomplete
        Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Path: VM > ${widget.state.parentLabel}',
                    style: Theme.of(context).textTheme.bodySmall,
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    'Parent: ${widget.state.parentLabel} (Depth ${widget.state.depth})',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            widget.state.missingSlots.isEmpty
                ? Chip(
                    label: const Text('Complete ✓'),
                    backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                  )
                : Chip(
                    label: Text('Missing: ${widget.state.missingSlots}'),
                    backgroundColor: Theme.of(context).colorScheme.errorContainer,
                  ),
            const SizedBox(width: 8),
            OutlinedButton.icon(
              onPressed: () {}, // TODO: Wire to parent widget's next incomplete handler
              icon: const Icon(Icons.skip_next),
              label: const Text('Next Incomplete'),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Conflict/Error Banner
        if (widget.state.banner != null) ...[
          Card(
            color: Theme.of(context).colorScheme.errorContainer,
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(
                children: [
                  const Icon(Icons.warning_amber, color: Colors.orange),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      widget.state.banner!.message,
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ),
                  if (widget.state.banner!.action != null) ...[
                    const SizedBox(width: 12),
                    OutlinedButton(
                      onPressed: widget.state.banner!.action,
                      child: Text(widget.state.banner!.actionLabel),
                    ),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
        ],
        Expanded(
          child: ListView.separated(
            itemCount: 5,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (_, i) {
              final s = widget.state.slots[i];
              return Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      SizedBox(
                        width: 40,
                        child: Text(
                          'Slot ${s.slot}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Stack(
                              children: [
                                TextField(
                                  key: ValueKey('slot_${s.slot}'),
                                  decoration: InputDecoration(
                                    labelText: 'Label',
                                    helperText: s.existing ? 'Existing' : 'Empty',
                                    errorText: s.error,
                                  ),
                                  controller: widget.controllers[s.slot]!,
                                  focusNode: widget.focusNodes[s.slot]!,
                                  textInputAction: TextInputAction.next,
                                  onChanged: (v) {
                                    widget.onChange(s.slot, v);
                                    widget.onDirtyChanged(true);
                                    setState(() {}); // updates counters/dup warnings
                                  },
                                ),
                                if (widget.focusNodes[s.slot]!.hasFocus &&
                                    widget.controllers[s.slot]!.text.trim().length >= 2)
                                  Positioned(
                                    left: 0,
                                    right: 0,
                                    top: 56, // Position below the TextField
                                    child: DictionarySuggestionsOverlay(
                                      type: 'node_label',
                                      currentText: widget.controllers[s.slot]!.text,
                                      onSuggestionSelected: (suggestion) {
                                        widget.controllers[s.slot]!.text = suggestion;
                                        widget.controllers[s.slot]!.selection =
                                            TextSelection.collapsed(offset: suggestion.length);
                                        widget.onChange(s.slot, suggestion);
                                        widget.onDirtyChanged(true);
                                        widget.focusNodes[s.slot]!.unfocus(); // Hide overlay
                                      },
                                      onDismiss: () {
                                        widget.focusNodes[s.slot]!.unfocus();
                                      },
                                    ),
                                  ),
                              ],
                            ),
                            if (s.error != null) ...[
                              const SizedBox(height: 4),
                              Text(
                                s.error!,
                                style: TextStyle(
                                  color: Theme.of(context).colorScheme.error,
                                  fontSize: 12,
                                ),
                              ),
                            ] else if (s.warning != null) ...[
                              const SizedBox(height: 4),
                              Row(
                                children: [
                                  Icon(
                                    Icons.warning_amber,
                                    size: 14,
                                    color: Theme.of(context).colorScheme.secondary,
                                  ),
                                  const SizedBox(width: 4),
                                  Expanded(
                                    child: Text(
                                      s.warning!,
                                      style: TextStyle(
                                        color: Theme.of(context).colorScheme.secondary,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            ElevatedButton.icon(
              onPressed: widget.state.saving ? null : widget.onSave,
              icon: const Icon(Icons.save),
              label: const Text('Save All  (Ctrl+S)'),
            ),
            const SizedBox(width: 8),
            OutlinedButton.icon(
              onPressed: widget.state.saving ? null : widget.onReset,
              icon: const Icon(Icons.refresh),
              label: const Text('Reset'),
            ),
            const SizedBox(width: 12),
            if (widget.state.missingSlots.isEmpty) const Chip(
              avatar: Icon(Icons.check, size: 16),
              label: Text('Complete'),
            ),
          ],
        ),
      ],
    );
  }
}

class _Footer extends StatelessWidget {
  final EditTreeState state;
  final VoidCallback onSave;
  final VoidCallback onReset;

  const _Footer({
    required this.state,
    required this.onSave,
    required this.onReset,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final filled = state.slots.where((s) => s.text.trim().isNotEmpty).length;
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        border: Border(top: BorderSide(color: Theme.of(context).dividerColor)),
      ),
      child: Row(
        children: [
          Text('Filled: $filled / 5'),
          const SizedBox(width: 12),
          if (state.saving) const Padding(
            padding: EdgeInsets.only(right: 12),
            child: SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)),
          ),
          const Spacer(),
          OutlinedButton(onPressed: state.saving ? null : onReset, child: const Text('Reset')),
          const SizedBox(width: 8),
          ElevatedButton(onPressed: state.saving ? null : onSave, child: const Text('Save All')),
        ],
      ),
    );
  }
}
