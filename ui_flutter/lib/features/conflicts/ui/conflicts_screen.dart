import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../state/conflicts_provider.dart';
import '../data/conflicts_repository.dart';
import 'widgets/label_chip.dart';

class ConflictsScreen extends ConsumerStatefulWidget {
  const ConflictsScreen({super.key});

  @override
  ConsumerState<ConflictsScreen> createState() => _ConflictsScreenState();
}

class _ConflictsScreenState extends ConsumerState<ConflictsScreen> {
  final TextEditingController _newLabelController = TextEditingController();

  @override
  void initState() {
    super.initState();
    // Load conflicts on init
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(conflictsListProvider.notifier).loadConflicts();
    });
  }

  @override
  void dispose() {
    _newLabelController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final conflictsState = ref.watch(conflictsListProvider);
    final groupState = ref.watch(conflictsGroupProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Conflicts'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            if (Navigator.of(context).canPop()) {
              Navigator.of(context).pop();
            } else {
              context.go('/workspace');
            }
          },
        ),
        actions: [
          // Progress HUD
          _buildProgressHUD(conflictsState),
          const SizedBox(width: 8),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.read(conflictsListProvider.notifier).refresh();
            },
          ),
        ],
      ),
      body: Row(
        children: [
          // Left pane: conflicts list
          Expanded(
            flex: 1,
            child: _buildConflictsList(conflictsState),
          ),
          const VerticalDivider(width: 1),
          // Right pane: group resolution
          Expanded(
            flex: 2,
            child: _buildGroupResolution(groupState),
          ),
        ],
      ),
    );
  }

  Widget _buildConflictsList(ConflictsListState state) {
    return Column(
      children: [
        if (state.loading) const LinearProgressIndicator(),
        if (state.error != null)
          Container(
            padding: const EdgeInsets.all(8),
            color: Colors.red.shade100,
            child: Text(
              state.error!,
              style: TextStyle(color: Colors.red.shade800),
            ),
          ),
        Expanded(
          child: ListView.builder(
            itemCount: state.items.length,
            itemBuilder: (context, index) {
              final item = state.items[index];
              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                child: ListTile(
                  title: Row(
                    children: [
                      Expanded(child: Text('${item.label} (id=${item.parentId})')),
                      _buildChildCountBadge(item.childCount),
                    ],
                  ),
                  subtitle: Text(
                    'duplicates=${item.duplicateParents} • variants=${item.variantSets} • slotDup=${item.slotDupCount} • null=${item.nullSlotCount}',
                  ),
                  onTap: () {
                    ref.read(conflictsGroupProvider.notifier).selectGroup(item.parentId);
                  },
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildGroupResolution(ConflictsGroupState state) {
    if (state.selectedGroupNodeId == null) {
      return const Center(
        child: Text('Select a conflict on the left.'),
      );
    }

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Parent ID: ${state.selectedGroupNodeId} • Choose exactly 5 children to keep',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 16),
          
          // Selection counter and confirm button
          Row(
            children: [
              Text('Selected: ${state.selectedLabels.length}/5'),
              const Spacer(),
              ElevatedButton.icon(
                onPressed: state.canConfirm && !state.loading
                    ? () => _handleResolve()
                    : null,
                icon: const Icon(Icons.done_all),
                label: const Text('Confirm'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // Inline add label
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _newLabelController,
                  decoration: const InputDecoration(
                    labelText: 'Add new child label',
                    border: OutlineInputBorder(),
                  ),
                  onSubmitted: (_) => _handleAddInlineLabel(),
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton.icon(
                onPressed: state.canAddInlineLabel ? _handleAddInlineLabel : null,
                icon: const Icon(Icons.add),
                label: const Text('Add'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // Children labels grid
          Expanded(
            child: state.loading
                ? const Center(child: CircularProgressIndicator())
                : _buildChildrenGrid(state),
          ),
          
          if (state.error != null)
            Container(
              padding: const EdgeInsets.all(8),
              color: Colors.red.shade100,
              child: Text(
                state.error!,
                style: TextStyle(color: Colors.red.shade800),
              ),
            ),
          
          const SizedBox(height: 8),
          const Text(
            'Tip: Choose the best five, then Confirm. All other children under the kept parent will be removed; duplicates will be merged.',
            style: TextStyle(fontSize: 12, color: Colors.grey),
          ),
        ],
      ),
    );
  }

  Widget _buildChildrenGrid(ConflictsGroupState state) {
    return GridView.builder(
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 4.5,
        crossAxisSpacing: 8,
        mainAxisSpacing: 8,
      ),
      itemCount: state.childrenLabels.length,
      itemBuilder: (context, index) {
        final child = state.childrenLabels[index];
        final isSelected = state.selectedLabels.contains(child.label);
        final isSynthetic = child.childId == -1;
        
        return LabelChip(
          label: child.label,
          slot: child.slot,
          fromId: child.fromId,
          isSelected: isSelected,
          isSynthetic: isSynthetic,
          onTap: () => _handleToggleLabel(child.label),
        );
      },
    );
  }

  void _handleToggleLabel(String label) {
    ref.read(conflictsGroupProvider.notifier).toggleLabel(label);
  }

  void _handleAddInlineLabel() {
    final label = _newLabelController.text.trim();
    if (label.isEmpty) return;
    
    ref.read(conflictsGroupProvider.notifier).setInlineNewLabel(label);
    ref.read(conflictsGroupProvider.notifier).addInlineLabel();
    _newLabelController.clear();
  }

  Future<void> _handleResolve() async {
    try {
      await ref.read(conflictsGroupProvider.notifier).resolveGroup();
      
      // Show success message
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Merge applied.')),
        );
      }
      
      // Refresh conflicts list
      ref.read(conflictsListProvider.notifier).refresh();
      
      // Clear group state
      ref.read(conflictsGroupProvider.notifier).clearGroup();
    } catch (e) {
      if (mounted) {
        _handleResolveError(e);
      }
    }
  }

  void _handleResolveError(dynamic error) {
    String message;
    bool showReload = false;
    
    if (error is ValidationException) {
      switch (error.type) {
        case 'must_choose_five':
          message = 'Choose exactly 5 labels.';
          break;
        case 'duplicate_labels':
          message = 'Labels must be unique.';
          break;
        case 'keep_id':
          message = 'Invalid keeper for this group.';
          break;
        default:
          message = error.message;
      }
    } else if (error is ConflictException) {
      message = error.message;
      showReload = true;
    } else {
      message = 'Error: ${error.toString()}';
    }
    
    if (showReload) {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Conflict'),
          content: Text(message),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                ref.read(conflictsListProvider.notifier).refresh();
              },
              child: const Text('Reload Latest'),
            ),
          ],
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    }
  }

  Widget _buildProgressHUD(ConflictsListState state) {
    final total = state.totalConflictsInitial ?? state.currentCount;
    final resolved = state.resolvedCount;
    final progress = state.progress;
    
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: 160,
          child: LinearProgressIndicator(
            value: progress,
            backgroundColor: Colors.grey.shade300,
            valueColor: AlwaysStoppedAnimation<Color>(
              progress == 1.0 ? Colors.green : Colors.blue,
            ),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          'Resolved $resolved of $total',
          style: const TextStyle(fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildChildCountBadge(int childCount) {
    final isExactFive = childCount == 5;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: isExactFive ? Colors.green.shade100 : Colors.grey.shade300,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isExactFive ? Colors.green : Colors.grey,
          width: 1,
        ),
      ),
      child: Text(
        '$childCount/5',
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          color: isExactFive ? Colors.green.shade800 : Colors.grey.shade600,
        ),
      ),
    );
  }
}
