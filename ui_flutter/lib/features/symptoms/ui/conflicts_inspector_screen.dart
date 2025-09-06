import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../widgets/layout/scroll_scaffold.dart';
import '../../../widgets/app_back_leading.dart';
import '../data/conflicts_service.dart';
import '../data/conflicts_models.dart';

class ConflictsInspectorScreen extends ConsumerStatefulWidget {
  const ConflictsInspectorScreen({super.key});

  @override
  ConsumerState<ConflictsInspectorScreen> createState() => _ConflictsInspectorScreenState();
}

class _ConflictsInspectorScreenState extends ConsumerState<ConflictsInspectorScreen>
    with TickerProviderStateMixin {
  late TabController _tabController;
  Map<ConflictType, List<ConflictItem>> _conflictsByType = {};
  Map<String, int> _conflictsSummary = {};
  bool _loading = false;
  String _searchQuery = '';
  int? _depthFilter;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: ConflictType.values.length, vsync: this);
    _loadConflicts();
    _loadSummary();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadConflicts() async {
    setState(() => _loading = true);

    try {
      final service = ref.read(conflictsServiceProvider);
      final allConflicts = <ConflictType, List<ConflictItem>>{};

      for (final type in ConflictType.values) {
        final conflicts = await service.getConflictsByType(
          type,
          depth: _depthFilter,
          query: _searchQuery.isNotEmpty ? _searchQuery : null,
        );
        allConflicts[type] = conflicts;
      }

      if (mounted) {
        setState(() {
          _conflictsByType = allConflicts;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _loading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load conflicts: $e')),
        );
      }
    }
  }

  Future<void> _loadSummary() async {
    try {
      final service = ref.read(conflictsServiceProvider);
      final summary = await service.getConflictsSummary();
      if (mounted) {
        setState(() => _conflictsSummary = summary);
      }
    } catch (e) {
      // Summary is optional, don't show error
    }
  }

  Future<void> _resolveConflict(ConflictItem conflict, String action, {String? newValue}) async {
    try {
      final service = ref.read(conflictsServiceProvider);
      final resolution = ConflictResolution(
        conflictId: conflict.id,
        action: action,
        newValue: newValue,
      );

      await service.resolveConflict(resolution);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Conflict resolved: $action')),
        );
        _loadConflicts();
        _loadSummary();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to resolve conflict: $e')),
        );
      }
    }
  }

  Future<void> _jumpToEditor(ConflictItem conflict) async {
    try {
      final service = ref.read(conflictsServiceProvider);
      final location = await service.jumpToConflictLocation(conflict.id);

      // Navigate to edit tree with the appropriate parent
      if (location['parent_id'] != null) {
        // This would navigate to the edit tree screen
        // For now, show a message
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Navigate to parent ${location['parent_id']}')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to jump to editor: $e')),
        );
      }
    }
  }

  void _showConflictDetails(ConflictItem conflict) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Conflict Details'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Type: ${conflict.type.name}'),
              Text('Description: ${conflict.description}'),
              if (conflict.parentId != null)
                Text('Parent ID: ${conflict.parentId}'),
              if (conflict.depth != null)
                Text('Depth: ${conflict.depth}'),
              const SizedBox(height: 16),
              const Text('Affected Labels:', style: TextStyle(fontWeight: FontWeight.bold)),
              ...conflict.affectedLabels.map((label) => Text('• $label')),
              const SizedBox(height: 16),
              const Text('Affected Nodes:', style: TextStyle(fontWeight: FontWeight.bold)),
              ...conflict.affectedNodes.map((nodeId) => Text('• Node $nodeId')),
              if (conflict.resolution != null) ...[
                const SizedBox(height: 16),
                Text('Resolution: ${conflict.resolution}'),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
          if (conflict.parentId != null)
            ElevatedButton.icon(
              onPressed: () {
                Navigator.of(context).pop();
                _jumpToEditor(conflict);
              },
              icon: const Icon(Icons.edit),
              label: const Text('Jump to Editor'),
            ),
        ],
      ),
    );
  }

  Widget _buildFilters() {
    return Card(
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
                  child: TextField(
                    decoration: const InputDecoration(
                      labelText: 'Search conflicts',
                      prefixIcon: Icon(Icons.search),
                    ),
                    onChanged: (value) {
                      _searchQuery = value;
                      _loadConflicts();
                    },
                  ),
                ),
                const SizedBox(width: 16),
                DropdownButton<int?>(
                  value: _depthFilter,
                  hint: const Text('All Depths'),
                  items: [
                    const DropdownMenuItem(value: null, child: Text('All Depths')),
                    ...List.generate(5, (i) => i + 1).map((depth) {
                      return DropdownMenuItem(
                        value: depth,
                        child: Text('Depth $depth'),
                      );
                    }),
                  ],
                  onChanged: (value) {
                    setState(() => _depthFilter = value);
                    _loadConflicts();
                  },
                ),
                const SizedBox(width: 16),
                ElevatedButton.icon(
                  onPressed: _loadConflicts,
                  icon: const Icon(Icons.refresh),
                  label: const Text('Refresh'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummary() {
    if (_conflictsSummary.isEmpty) return const SizedBox.shrink();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Summary', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            Wrap(
              spacing: 16,
              runSpacing: 8,
              children: ConflictType.values.map((type) {
                final count = _conflictsSummary[type.name] ?? 0;
                return Chip(
                  label: Text('${type.name}: $count'),
                  backgroundColor: _getConflictColor(type),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConflictsList(ConflictType type) {
    final conflicts = _conflictsByType[type] ?? [];

    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (conflicts.isEmpty) {
      return Center(
        child: Text('No ${type.name} conflicts found'),
      );
    }

    return ListView.builder(
      itemCount: conflicts.length,
      itemBuilder: (context, index) {
        final conflict = conflicts[index];
        return Card(
          child: ListTile(
            leading: Icon(_getConflictIcon(type), color: _getConflictColor(type)),
            title: Text(conflict.description),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (conflict.parentId != null)
                  Text('Parent: ${conflict.parentId}'),
                Text('Affected: ${conflict.affectedNodes.length} nodes'),
              ],
            ),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                IconButton(
                  icon: const Icon(Icons.info_outline),
                  onPressed: () => _showConflictDetails(conflict),
                  tooltip: 'Details',
                ),
                if (conflict.parentId != null)
                  IconButton(
                    icon: const Icon(Icons.edit),
                    onPressed: () => _jumpToEditor(conflict),
                    tooltip: 'Jump to Editor',
                  ),
                IconButton(
                  icon: const Icon(Icons.check_circle_outline),
                  onPressed: () => _showResolutionDialog(conflict),
                  tooltip: 'Resolve',
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showResolutionDialog(ConflictItem conflict) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Resolve Conflict'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(conflict.description),
            const SizedBox(height: 16),
            const Text('Choose resolution action:'),
            const SizedBox(height: 8),
            // This would be populated with actual resolution options
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                _resolveConflict(conflict, 'auto_resolve');
              },
              child: const Text('Auto Resolve'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
        ],
      ),
    );
  }

  IconData _getConflictIcon(ConflictType type) {
    switch (type) {
      case ConflictType.duplicateLabels:
        return Icons.copy;
      case ConflictType.orphans:
        return Icons.broken_image;
      case ConflictType.depthAnomalies:
        return Icons.layers;
      case ConflictType.missingSlots:
        return Icons.warning;
      case ConflictType.invalidReferences:
        return Icons.link_off;
    }
  }

  Color _getConflictColor(ConflictType type) {
    switch (type) {
      case ConflictType.duplicateLabels:
        return Colors.orange;
      case ConflictType.orphans:
        return Colors.red;
      case ConflictType.depthAnomalies:
        return Colors.blue;
      case ConflictType.missingSlots:
        return Colors.amber;
      case ConflictType.invalidReferences:
        return Colors.purple;
    }
  }

  @override
  Widget build(BuildContext context) {
    return ScrollScaffold(
      title: 'Conflicts Inspector',
      leading: const AppBackLeading(),
      children: [
        // Summary
        _buildSummary(),
        const SizedBox(height: 16),

        // Filters
        _buildFilters(),
        const SizedBox(height: 16),

        // Tabs
        Card(
          child: Column(
            children: [
              TabBar(
                controller: _tabController,
                tabs: ConflictType.values.map((type) {
                  final count = _conflictsByType[type]?.length ?? 0;
                  return Tab(
                    text: '${type.name} (${count})',
                    icon: Icon(_getConflictIcon(type)),
                  );
                }).toList(),
                isScrollable: true,
              ),
              SizedBox(
                height: 400,
                child: TabBarView(
                  controller: _tabController,
                  children: ConflictType.values.map((type) => _buildConflictsList(type)).toList(),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
