import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../widgets/layout/scroll_scaffold.dart';
import '../../../widgets/app_back_leading.dart';
import '../data/symptoms_repository.dart';
import '../data/symptoms_models.dart';

// Enhanced Symptoms Screen for Phase-6E
class SymptomsScreen extends ConsumerStatefulWidget {
  const SymptomsScreen({super.key});

  @override
  ConsumerState<SymptomsScreen> createState() => _SymptomsScreenState();
}

class _SymptomsScreenState extends ConsumerState<SymptomsScreen>
    with TickerProviderStateMixin {
  // Level picker and filtering
  int _selectedLevel = 1;
  bool _compactMode = false;
  SortMode _sortMode = SortMode.issuesFirst;

  // Search and pagination
  final TextEditingController _searchController = TextEditingController();
  List<IncompleteParent> _parents = [];
  bool _loading = false;
  bool _loadingMore = false;
  bool _hasMore = true;
  int _offset = 0;
  final int _limit = 50;
  Timer? _searchDebounceTimer;

  // Auto dictionary sync
  bool _autoDictionarySync = true;

  // Current parent editing state
  IncompleteParent? _selectedParent;
  ParentChildren? _currentParentData;
  bool _editingParent = false;
  final Map<int, TextEditingController> _slotControllers = {};
  final Map<int, FocusNode> _slotFocusNodes = {};

  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadParents();

    // Initialize slot controllers and focus nodes
    for (int i = 1; i <= 5; i++) {
      _slotControllers[i] = TextEditingController();
      _slotFocusNodes[i] = FocusNode();
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    _searchDebounceTimer?.cancel();
    _tabController.dispose();
    for (final controller in _slotControllers.values) {
      controller.dispose();
    }
    for (final focusNode in _slotFocusNodes.values) {
      focusNode.dispose();
    }
    super.dispose();
  }

  Future<void> _loadParents({bool append = false}) async {
    if (_loadingMore && append) return;

    setState(() {
      if (append) {
        _loadingMore = true;
      } else {
        _loading = true;
        _offset = 0;
        _hasMore = true;
      }
    });

    try {
      final repo = ref.read(symptomsRepositoryProvider);
      final parents = await repo.getIncompleteParents(
        depth: _selectedLevel,
        query: _searchController.text.trim().isNotEmpty
            ? _searchController.text.trim()
            : null,
        limit: _limit,
        offset: append ? _offset : 0,
        sortMode: _sortMode,
      );

      if (mounted) {
        setState(() {
          if (append) {
            _parents.addAll(parents);
            _offset += _limit;
            _loadingMore = false;
          } else {
            _parents = parents;
            _offset = _limit;
            _loading = false;
          }
          _hasMore = parents.length == _limit;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _loadingMore = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load parents: $e')),
        );
      }
    }
  }

  void _onSearchChanged(String query) {
    _searchDebounceTimer?.cancel();
    _searchDebounceTimer = Timer(const Duration(milliseconds: 300), () {
      _loadParents();
    });
  }

  Future<void> _selectParent(IncompleteParent parent) async {
    setState(() {
      _selectedParent = parent;
      _editingParent = true;
    });

    try {
      final repo = ref.read(symptomsRepositoryProvider);
      final parentData = await repo.getParentChildren(parent.parentId);

      if (mounted) {
        setState(() => _currentParentData = parentData);

        // Populate controllers with existing data
        for (final slot in parentData.children) {
          _slotControllers[slot.slot]?.text = slot.label ?? '';
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load parent data: $e')),
        );
      }
    }
  }

  Future<void> _saveParent() async {
    if (_currentParentData == null) return;

    final children = <ChildSlot>[];
    for (int i = 1; i <= 5; i++) {
      final label = _slotControllers[i]?.text.trim();
      children.add(ChildSlot(
        slot: i,
        label: label?.isNotEmpty == true ? label : null,
      ));
    }

    try {
      final repo = ref.read(symptomsRepositoryProvider);
      await repo.updateParentChildren(
        _currentParentData!.parentId,
        children,
        version: _currentParentData!.version,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Parent updated successfully')),
        );
        _loadParents(); // Refresh the list
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to update parent: $e')),
        );
      }
    }
  }

  Future<void> _materializeParent() async {
    if (_currentParentData == null) return;

    try {
      final repo = ref.read(symptomsRepositoryProvider);
      final result = await repo.materializeParent(_currentParentData!.parentId);

      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Materialization Complete'),
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
                  const Text('Log:',
                      style: TextStyle(fontWeight: FontWeight.bold)),
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
        _loadParents(); // Refresh the list
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to materialize: $e')),
        );
      }
    }
  }

  Widget _buildLevelPicker() {
    return Row(
      children: [
        const Text('Level:', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(width: 8),
        DropdownButton<int>(
          value: _selectedLevel,
          items: List.generate(5, (i) => i + 1).map((level) {
            return DropdownMenuItem(
              value: level,
              child: Text('Node $level'),
            );
          }).toList(),
          onChanged: (value) {
            if (value != null) {
              setState(() => _selectedLevel = value);
              _loadParents();
            }
          },
        ),
        const SizedBox(width: 16),
        const Text('Sort:', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(width: 8),
        DropdownButton<SortMode>(
          value: _sortMode,
          items: SortMode.values.map((mode) {
            return DropdownMenuItem(
              value: mode,
              child: Text(mode.name.replaceAll('_', ' ').toUpperCase()),
            );
          }).toList(),
          onChanged: (value) {
            if (value != null) {
              setState(() => _sortMode = value);
              _loadParents();
            }
          },
        ),
      ],
    );
  }

  Widget _buildSearchBar() {
    return Row(
      children: [
        Expanded(
          child: TextField(
            controller: _searchController,
            decoration: const InputDecoration(
              prefixIcon: Icon(Icons.search),
              labelText: 'Search parents',
              hintText: 'Enter parent label...',
            ),
            onChanged: _onSearchChanged,
          ),
        ),
        const SizedBox(width: 8),
        IconButton(
          icon: Icon(_compactMode ? Icons.view_list : Icons.view_compact),
          onPressed: () => setState(() => _compactMode = !_compactMode),
          tooltip: _compactMode ? 'Normal view' : 'Compact view',
        ),
      ],
    );
  }

  Widget _buildParentList() {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_parents.isEmpty) {
      return const Center(
        child: Text('No incomplete parents found'),
      );
    }

    return ListView.builder(
      itemCount: _parents.length + (_loadingMore ? 1 : 0),
      itemBuilder: (context, index) {
        if (index == _parents.length) {
          return const Center(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: CircularProgressIndicator(),
            ),
          );
        }

        final parent = _parents[index];
        final isSelected = _selectedParent?.parentId == parent.parentId;

        return Card(
          color: isSelected
              ? Theme.of(context).colorScheme.primaryContainer
              : null,
          child: ListTile(
            title: Text(parent.label),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                    'Depth ${parent.depth} • Missing: ${parent.missingSlots.join(", ")}'),
                Text('Updated: ${parent.updatedAt.toString().split('T')[0]}'),
                _buildParentStatus(parent),
              ],
            ),
            trailing: _buildParentStatusChip(parent),
            onTap: () => _selectParent(parent),
            selected: isSelected,
          ),
        );
      },
    );
  }

  Widget _buildParentStatus(IncompleteParent parent) {
    final filled = 5 - parent.missingSlots.length;
    final status = _getParentStatus(filled);

    return Text(
      'Status: $status ($filled/5 filled)',
      style: TextStyle(
        color: _getStatusColor(status),
        fontSize: 12,
      ),
    );
  }

  Widget _buildParentStatusChip(IncompleteParent parent) {
    final filled = 5 - parent.missingSlots.length;
    final status = _getParentStatus(filled);

    return Chip(
      label: Text(status),
      backgroundColor: _getStatusColor(status).withOpacity(0.1),
      side: BorderSide(color: _getStatusColor(status)),
    );
  }

  String _getParentStatus(int filled) {
    if (filled == 0) return 'No group';
    if (filled < 5) return 'Symptom left out';
    if (filled == 5) return 'OK';
    return 'Overspecified';
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'OK':
        return Colors.green;
      case 'Symptom left out':
        return Colors.orange;
      case 'No group':
        return Colors.red;
      case 'Overspecified':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  Widget _buildEditorPane() {
    if (!_editingParent || _currentParentData == null) {
      return const Center(
        child: Text('Select a parent to edit'),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _currentParentData!.parentLabel,
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                Text('Path: ${_currentParentData!.path}'),
                Text(
                    'Missing slots: ${_currentParentData!.missingSlots.join(", ")}'),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Slot editors
        ...List.generate(5, (index) {
          final slot = index + 1;
          final childSlot = _currentParentData!.children.firstWhere(
            (c) => c.slot == slot,
            orElse: () => ChildSlot(slot: slot),
          );

          return Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Slot $slot',
                      style: const TextStyle(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _slotControllers[slot],
                    focusNode: _slotFocusNodes[slot],
                    decoration: InputDecoration(
                      labelText: 'Label',
                      helperText:
                          childSlot.existing == true ? 'Existing' : 'Empty',
                      errorText: childSlot.error,
                      border: const OutlineInputBorder(),
                    ),
                    onChanged: (_) => setState(() {}),
                  ),
                  if (childSlot.warning != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      childSlot.warning!,
                      style:
                          const TextStyle(color: Colors.orange, fontSize: 12),
                    ),
                  ],
                ],
              ),
            ),
          );
        }),

        const SizedBox(height: 16),

        // Action buttons
        Row(
          children: [
            ElevatedButton.icon(
              onPressed: _saveParent,
              icon: const Icon(Icons.save),
              label: const Text('Save'),
            ),
            const SizedBox(width: 8),
            ElevatedButton.icon(
              onPressed: _materializeParent,
              icon: const Icon(Icons.build),
              label: const Text('Materialize'),
            ),
            const SizedBox(width: 8),
            Switch(
              value: _autoDictionarySync,
              onChanged: (value) => setState(() => _autoDictionarySync = value),
            ),
            const Text('Auto Dictionary Sync'),
          ],
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return ScrollScaffold(
      title: 'Symptoms Editor',
      leading: const AppBackLeading(),
      children: [
        // Level picker and controls
        _buildLevelPicker(),
        const SizedBox(height: 16),

        // Search bar
        _buildSearchBar(),
        const SizedBox(height: 16),

        // Main content
        Expanded(
          child: Row(
            children: [
              // Parent list
              Expanded(
                flex: 2,
                child: Column(
                  children: [
                    Text(
                      '${_parents.length} parents found',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    Expanded(child: _buildParentList()),
                  ],
                ),
              ),

              const VerticalDivider(width: 1),

              // Editor pane
              Expanded(
                flex: 3,
                child: _buildEditorPane(),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
