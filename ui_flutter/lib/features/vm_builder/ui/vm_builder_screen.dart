import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:typed_data';
import '../state/vm_provider.dart';

class VmBuilderScreen extends StatefulWidget {
  final String baseUrl;
  final int? initialParentId;
  final VoidCallback? onParentNavigated;
  const VmBuilderScreen({
    super.key,
    required this.baseUrl,
    this.initialParentId,
    this.onParentNavigated,
  });

  @override
  State<VmBuilderScreen> createState() => _VmBuilderScreenState();
}

class _VmBuilderScreenState extends State<VmBuilderScreen> {
  final _newChildCtrl = TextEditingController();
  final _searchCtrl = TextEditingController();

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

      // Navigate to specific parent if provided
      if (widget.initialParentId != null) {
        _navigateToParent(widget.initialParentId!);
      }
    });
  }

  Future<void> _navigateToParent(int parentId) async {
    final state = context.read<VmState>();
    try {
      // Try to navigate to the specific parent
      await state.navigateToParentById(parentId);
      widget.onParentNavigated?.call();
    } catch (e) {
      // If navigation fails, show a message
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not navigate to parent #$parentId: $e')),
        );
      }
      widget.onParentNavigated?.call();
    }
  }

  Future<void> _searchParent(VmState state, String searchText) async {
    final parentIdStr = searchText.trim();
    if (parentIdStr.isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please enter a parent ID to search')),
        );
      }
      return;
    }

    final parentId = int.tryParse(parentIdStr);
    if (parentId == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please enter a valid parent ID number')),
        );
      }
      return;
    }

    try {
      await state.navigateToParentById(parentId);
      _searchCtrl.clear(); // Clear the search field on success
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Navigated to parent #$parentId')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Parent #$parentId not found: $e')),
        );
      }
    }
  }

  Future<void> _showRenameDialog(VmState state) async {
    final controller = TextEditingController(text: state.currentParentLabel);

    final result = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Rename Parent'),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: const InputDecoration(
            labelText: 'Parent name',
            hintText: 'Enter new parent name',
            border: OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(controller.text.trim()),
            child: const Text('Rename'),
          ),
        ],
      ),
    );

    if (result != null && result.isNotEmpty && result != state.currentParentLabel) {
      await _handleParentRename(state, result);
    }
  }

  Future<void> _handleParentRename(VmState state, String newName) async {
    try {
      // First check if a parent with this name already exists
      final existingParents = await state.repo.findParentsByLabel(newName);

      if (existingParents.isNotEmpty) {
        // Show merge confirmation dialog
        await _showMergeDialog(state, newName, existingParents);
      } else {
        // Simple rename - no conflicts
        await state.renameParent(state.currentParentId!, newName);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Parent renamed to "$newName"')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to rename parent: $e')),
        );
      }
    }
  }

  Future<void> _showMergeDialog(VmState state, String newName, List<Map<String, dynamic>> existingParents) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Merge Parents'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('A parent named "$newName" already exists. Do you want to merge the children?'),
            const SizedBox(height: 16),
            const Text('Existing parent:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text('Parent #${existingParents.first['id']} at depth ${existingParents.first['depth']}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Merge'),
          ),
        ],
      ),
    );

    if (result == true) {
      await _handleParentMerge(state, newName, existingParents.first);
    }
  }

  Future<void> _handleParentMerge(VmState state, String newName, Map<String, dynamic> existingParent) async {
    try {
      // Get children from both parents
      final currentChildren = await state.repo.getChildren(state.currentParentId!);
      final existingChildren = await state.repo.getChildren(existingParent['id'] as int);

      // Combine all unique children
      final allChildren = <String>{};
      allChildren.addAll(currentChildren.map((c) => c['label'] as String));
      allChildren.addAll(existingChildren.map((c) => c['label'] as String));

      if (allChildren.length <= 5) {
        // Simple merge - no need for selection
        await state.mergeParents(state.currentParentId!, existingParent['id'] as int, allChildren.toList());
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Parents merged successfully')),
          );
        }
      } else {
        // Need to select which 5 children to keep
        await _showChildrenSelectionDialog(state, newName, existingParent, allChildren.toList());
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to merge parents: $e')),
        );
      }
    }
  }

  Future<void> _showChildrenSelectionDialog(VmState state, String newName, Map<String, dynamic> existingParent, List<String> allChildren) async {
    final selectedChildren = <String>{};
    bool isMerging = false;

    final result = await showDialog<List<String>>(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('Select Children'),
          content: SizedBox(
            width: double.maxFinite,
            height: 300,
            child: Column(
              children: [
                Text('Both parents have children. Select exactly 5 to keep:'),
                const SizedBox(height: 16),
                Expanded(
                  child: ListView.builder(
                    itemCount: allChildren.length,
                    itemBuilder: (context, index) {
                      final child = allChildren[index];
                      final isSelected = selectedChildren.contains(child);
                      final canSelect = selectedChildren.length < 5 || isSelected;

                      return CheckboxListTile(
                        title: Text(child),
                        value: isSelected,
                        enabled: canSelect,
                        onChanged: (value) {
                          setState(() {
                            if (value == true) {
                              selectedChildren.add(child);
                            } else {
                              selectedChildren.remove(child);
                            }
                          });
                        },
                      );
                    },
                  ),
                ),
                Text('Selected: ${selectedChildren.length}/5'),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: isMerging ? null : () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: (selectedChildren.length == 5 && !isMerging)
                  ? () async {
                      setState(() => isMerging = true);
                      try {
                        await state.mergeParents(state.currentParentId!, existingParent['id'] as int, selectedChildren.toList());
                        if (context.mounted) {
                          Navigator.of(context).pop(selectedChildren.toList());
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Parents merged successfully!')),
                          );
                        }
                      } catch (e) {
                        setState(() => isMerging = false);
                        if (context.mounted) {
                          String errorMessage = 'Failed to merge parents';
                          if (e.toString().contains('404')) {
                            errorMessage = 'One or both parents no longer exist. Please refresh and try again.';
                          } else if (e.toString().contains('500')) {
                            errorMessage = 'Server error during merge. Please try again.';
                          } else {
                            errorMessage = 'Failed to merge parents: ${e.toString()}';
                          }
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(errorMessage),
                              backgroundColor: Colors.red,
                            ),
                          );
                        }
                      }
                    }
                  : null,
              child: isMerging
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Merge'),
            ),
          ],
        ),
      ),
    );

  }

  @override
  void dispose() {
    _newChildCtrl.dispose();
    _searchCtrl.dispose();
    super.dispose();
  }

  Widget _importPanel(VmState s) {
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
                          groupValue: s.importMode,
                          onChanged: s.importing ? null : (v) => s.setImportMode(v),
                          materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        const Flexible(child: Text('Replace')),
                        const SizedBox(width: 8),
                        Radio<String>(
                          value: 'append',
                          groupValue: s.importMode,
                          onChanged: s.importing ? null : (v) => s.setImportMode(v),
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
                    await s.importBytes(s.importMode, bytes, f.name);
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
                  // Search section
                  const SizedBox(height: 12),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Search Parent', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              Expanded(
                                child: TextField(
                                  controller: _searchCtrl,
                                  decoration: const InputDecoration(
                                    labelText: 'Parent ID (e.g., 106)',
                                    hintText: 'Enter parent ID to search',
                                    border: OutlineInputBorder(),
                                    prefixIcon: Icon(Icons.search),
                                  ),
                                  keyboardType: TextInputType.number,
                                  onSubmitted: (value) => _searchParent(s, value),
                                ),
                              ),
                              const SizedBox(width: 8),
                              FilledButton.icon(
                                onPressed: () => _searchParent(s, _searchCtrl.text),
                                icon: const Icon(Icons.search),
                                label: const Text('Search'),
                              ),
                            ],
                          ),
                        ],
                      ),
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
                        Row(
                          children: [
                            Expanded(
                              child: Text('Parent: ${s.currentParentLabel} (${s.children.length}/5)', style: Theme.of(context).textTheme.titleLarge),
                            ),
                            IconButton(
                              icon: const Icon(Icons.edit),
                              tooltip: 'Edit parent name',
                              onPressed: () => _showRenameDialog(s),
                            ),
                          ],
                        ),
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
                                      onPressed: () async {
                                        final parentId = s.currentParentId!;
                                        final nodeId = child['id'] as int;
                                        await s.deleteNodeWithUndo(nodeId, parentId: parentId);
                                        if (context.mounted) {
                                          ScaffoldMessenger.of(context).showSnackBar(
                                            SnackBar(
                                              content: const Text('Node deleted'),
                                              action: SnackBarAction(
                                                label: 'Undo',
                                                onPressed: () async {
                                                  await s.undoLastDelete(parentId: parentId);
                                                },
                                              ),
                                              duration: const Duration(seconds: 6),
                                            ),
                                          );
                                        }
                                      },
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
