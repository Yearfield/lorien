import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/edit_tree_provider.dart';
import '../data/edit_tree_repository.dart';
import '../state/edit_tree_controller.dart';
import '../state/edit_tree_state.dart';

class EditTreeScreen extends ConsumerStatefulWidget {
  const EditTreeScreen({super.key});

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

  Future<void> _loadList() async {
    setState(() => _loadingList = true);
    final repo = ref.read(editTreeRepositoryProvider);
    final page = await repo.listIncomplete(
      query: _searchController.text,
      depth: _depth,
      limit: _limit,
      offset: _offset,
    );
    setState(() {
      _items = page.items;
      _total = page.total;
      _loadingList = false;
    });
  }

  Future<void> _nextIncomplete() async {
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

  Future<void> _openParent(
    int parentId,
    String label,
    int depth,
    String missing,
  ) async {
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
    // For now, call the existing _nextIncomplete method
    // Later this will be enhanced with unsaved guard
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
    _loadList();
  }

  @override
  void dispose() {
    for (final c in _controllers.values) c.dispose();
    for (final f in _focusNodes.values) f.dispose();
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
                    onChanged: (_) {
                      _offset = 0;
                      _loadList();
                    },
                  ),
                ),
                const SizedBox(width: 8),
                DropdownButton<int?>(
                  value: _depth,
                  hint: const Text('Depth'),
                  onChanged: (v) {
                    setState(() => _depth = v);
                    _offset = 0;
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
            child: Row(
              children: [
                ElevatedButton.icon(
                  onPressed: _onNextIncompleteTap,
                  icon: const Icon(Icons.skip_next),
                  label: const Text('Next Incomplete'),
                ),
                const Spacer(),
                Text('$_total found'),
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: _loadingList
                ? const Center(child: CircularProgressIndicator())
                : ListView.separated(
                    itemCount: _items.length,
                    separatorBuilder: (_, __) => const Divider(height: 1),
                    itemBuilder: (_, i) {
                      final it = _items[i];
                      return ListTile(
                        title: Text(it.label),
                        subtitle: Text(
                          'Depth ${it.depth} • Missing: ${it.missingSlots.isEmpty ? "—" : it.missingSlots}',
                        ),
                        onTap: () => _openParent(
                          it.parentId,
                          it.label,
                          it.depth,
                          it.missingSlots,
                        ),
                      );
                    },
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
          body: Row(
            children: [
              // Left Pane
              Flexible(
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
                              onChanged: (_) {
                                _offset = 0;
                                _loadList();
                              },
                            ),
                          ),
                          const SizedBox(width: 8),
                          DropdownButton<int?>(
                            value: _depth,
                            hint: const Text('Depth'),
                            onChanged: (v) {
                              setState(() => _depth = v);
                              _offset = 0;
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
                      child: Row(
                        children: [
                          ElevatedButton.icon(
                            onPressed: _nextIncomplete,
                            icon: const Icon(Icons.skip_next),
                            label: const Text('Next Incomplete'),
                          ),
                          const Spacer(),
                          Text('$_total found'),
                        ],
                      ),
                    ),
                    const Divider(height: 1),
                    Expanded(
                      child: _loadingList
                          ? const Center(child: CircularProgressIndicator())
                          : ListView.separated(
                              itemCount: _items.length,
                              separatorBuilder: (_, __) => const Divider(height: 1),
                              itemBuilder: (_, i) {
                                final it = _items[i];
                                return ListTile(
                                  title: Text(it.label),
                                  subtitle: Text(
                                    'Depth ${it.depth} • Missing: ${it.missingSlots.isEmpty ? "—" : it.missingSlots}',
                                  ),
                                  onTap: () => _openParent(
                                    it.parentId,
                                    it.label,
                                    it.depth,
                                    it.missingSlots,
                                  ),
                                );
                              },
                            ),
                    ),
                  ],
                ),
              ),
              VerticalDivider(width: 1, thickness: 1, color: Theme.of(context).dividerColor),
              // Right Pane
              Flexible(
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
              ),
            ],
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
