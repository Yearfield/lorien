import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import '../data/vm_repo.dart';

class VmState extends ChangeNotifier {
  final VmRepo repo;
  VmState(this.repo);

  // Toast callback function
  Function(String)? toast;

  bool isBusy = false;
  String? bannerError;

  List<Map<String, dynamic>> roots = [];
  int? currentParentId;
  String? currentParentLabel;
  List<String> children = [];
  bool loading = false;
  int currentDepth = 0;

  // Simple breadcrumb stack of visited parents (id,label,depth)
  final List<Map<String, dynamic>> crumbs = [];
  bool importing = false;
  String? importStatus; // "Imported 1292 rows (replace)" or error text

  // New features state
  bool filterOnlyRed = false;
  List<Map<String, dynamic>> childrenWithMeta = []; // children with red_flag info
  bool exporting = false;
  String importMode = 'replace';

  // Undo functionality
  Map<String, dynamic>? lastDeleteSnapshot;

  Future<void> loadRoots() async {
    isBusy = true; bannerError = null; notifyListeners();
    try {
      roots = await repo.getRoots();
      crumbs.clear();
      currentParentId = null;
      currentParentLabel = null;
      children = [];
    } catch (e) {
      bannerError = e.toString();
    } finally {
      isBusy = false; notifyListeners();
    }
  }

  Future<void> selectParent(int id, String label, int depth) async {
    currentParentId = id;
    currentParentLabel = label;
    currentDepth = depth;
    // push crumb
    crumbs.removeWhere((e) => e['id'] == id);
    crumbs.add({'id': id, 'label': label, 'depth': depth});
    await reloadChildren();
  }

  Future<void> navigateToParentById(int parentId) async {
    // Try to find the parent in the current roots first
    final root = roots.where((r) => r['id'] == parentId).firstOrNull;
    if (root != null) {
      await selectParent(parentId, root['label'] as String, 0);
      return;
    }

    // If not found in roots, try to get parent info from API
    try {
      final parentInfo = await repo.getParentInfo(parentId);
      if (parentInfo != null) {
        await selectParent(parentId, parentInfo['label'] as String, parentInfo['depth'] as int);
        return;
      }
    } catch (e) {
      // Parent not found or API error
    }

    throw Exception('Parent #$parentId not found');
  }

  Future<void> renameParent(int parentId, String newName) async {
    await repo.renameParent(parentId, newName);
    // Update local state
    if (currentParentId == parentId) {
      currentParentLabel = newName;
      notifyListeners();
    }
    // Update roots if this is a root
    final rootIndex = roots.indexWhere((r) => r['id'] == parentId);
    if (rootIndex != -1) {
      roots[rootIndex]['label'] = newName;
      notifyListeners();
    }
  }

  Future<void> mergeParents(int currentParentId, int existingParentId, List<String> selectedChildren) async {
    try {
      await repo.mergeParents(currentParentId, existingParentId, selectedChildren);
      // Navigate to the existing parent after merge
      await navigateToParentById(existingParentId);
      // Refresh the roots list to update any references
      await loadRoots();
    } catch (e) {
      // If merge fails, refresh the current state to avoid stale data
      if (currentParentId != null) {
        await reloadChildren();
      }
      rethrow;
    }
  }

  Future<void> reloadChildren() async {
    if (currentParentId == null) return;
    loading = true;
    notifyListeners();
    try {
      final ch = await repo.getChildren(currentParentId!, onlyRed: filterOnlyRed);
      childrenWithMeta = ch;
      children = ch.map((e) => (e['label'] as String)).toList();
    } catch (e) {
      // Handle error silently for now
      childrenWithMeta = [];
      children = [];
      toast?.call('Error reloading children: $e');
    }
    loading = false;
    notifyListeners();
  }

  void addChildLabel(String label) {
    if (label.trim().isEmpty) return;
    final trimmedLabel = label.trim();
    children = [...children, trimmedLabel];
    // Also update childrenWithMeta to include the new child
    childrenWithMeta = [...childrenWithMeta, {
      'label': trimmedLabel,
      'id': null, // Will be assigned when saved to server
      'red_flag': false,
    }];
    notifyListeners();
  }

  void removeChildAt(int idx) {
    children = [...children]..removeAt(idx);
    // Also update childrenWithMeta to keep them in sync
    childrenWithMeta = [...childrenWithMeta]..removeAt(idx);
    notifyListeners();
  }

  Future<void> save() async {
    if (loading) return;
    loading = true;
    notifyListeners();

    try {
      if (currentParentId == null) {
        toast?.call('No parent selected');
        return;
      }

      // Get current server state
      final serverChildren = await repo.getChildren(currentParentId!);
      final serverLabels = serverChildren.map((child) => child['label'] as String).toList();

      // Find new children (those not in server)
      final newChildren = children.where((child) => !serverLabels.contains(child)).toList();

      if (newChildren.isEmpty) {
        toast?.call('No changes to save');
        return;
      }

      // Add each new child using the simple API endpoint
      int successCount = 0;
      for (final childLabel in newChildren) {
        try {
          await repo.addChild(currentParentId!, childLabel);
          successCount++;
        } catch (e) {
          final errorMsg = e.toString();
          if (errorMsg.contains('parent already has 5 children')) {
            toast?.call('Cannot add "$childLabel": Parent already has 5 children. Please delete a child first or use a different parent.');
          } else {
            toast?.call('Failed to add "$childLabel": $errorMsg');
          }
        }
      }

      if (successCount > 0) {
        toast?.call('$successCount child(ren) added successfully');

        // Reload children to get fresh data with IDs
        await reloadChildren();
      }
    } catch (e) {
      toast?.call('Save failed: $e');
    } finally {
      loading = false;
      notifyListeners();
    }
  }



  Future<void> drillIntoChildByIndex(int index) async {
    if (index < 0 || index >= childrenWithMeta.length) {
      toast?.call('Invalid child index: $index');
      return;
    }

    final child = childrenWithMeta[index];
    final childId = child['id'] as int?;
    final childLabel = child['label'] as String;

    if (childId == null) {
      toast?.call('Child has no ID - please save changes first');
      return;
    }

    // Drill down into the child to show its children
    try {
      await selectParent(childId, childLabel, currentDepth + 1);
      toast?.call('Navigated to $childLabel');
    } catch (e) {
      toast?.call('Failed to navigate to $childLabel: $e');
    }
  }

  Future<void> drillDownChild(int childId, String childLabel) async {
    toast?.call('Starting drill down for $childLabel...');

    // Find clone candidates for this specific child
    final items = await repo.findCloneCandidates(childLabel);
    if (items.isEmpty) {
      toast?.call('No subtrees found for "$childLabel"');
      return;
    }

    // Filter out the current child to avoid circular references
    final filteredItems = items.where((item) => item['id'] != childId).toList();

    if (filteredItems.isEmpty) {
      toast?.call('No other parents found with label "$childLabel" to clone from');
      return;
    }

    // If multiple candidates, show selection dialog
    Map<String, dynamic>? selectedItem;
    if (filteredItems.length == 1) {
      selectedItem = filteredItems.first;
    } else {
      // For now, just use the first item if multiple exist
      selectedItem = filteredItems.first;
      toast?.call('Multiple parents found for "$childLabel", using first one');
    }

    final srcId = selectedItem['id'] as int?;
    if (srcId == null) {
      toast?.call('Invalid source ID for clone operation');
      return;
    }

    try {
      // Get the children of the source parent to clone from
      final sourceChildren = await repo.getChildren(srcId);
      if (sourceChildren.isEmpty) {
        toast?.call('No children found in source subtree for "$childLabel"');
        return;
      }

      // Clone each child from the source into the destination
      int clonedCount = 0;
      for (var sourceChild in sourceChildren) {
        try {
          await repo.addChild(childId, sourceChild['label'] as String);
          clonedCount++;
        } catch (e) {
          // Skip if child already exists or other error
          continue;
        }
      }

      toast?.call('Cloned $clonedCount children for "$childLabel"');

      // Navigate to the child to show the drilled down results
      await selectParent(childId, childLabel, currentDepth + 1);
      toast?.call('Navigated to $childLabel to show drilled down children');

    } catch (e) {
      final errorMsg = e.toString();
      if (errorMsg.contains('max_children_exceeded') || errorMsg.contains('destination parent already has 5 children')) {
        toast?.call('Cannot drill down: $childLabel already has 5 children');
      } else if (errorMsg.contains('depth_limit_exceeded') || errorMsg.contains('cloned subtree would exceed depth limit')) {
        // Just add as simple child when depth limit is reached
        try {
          await repo.addChild(childId, childLabel);
          toast?.call('Added "$childLabel" as simple child (depth limit reached)');

          // Navigate to the child to show the result
          await selectParent(childId, childLabel, currentDepth + 1);
        } catch (partialError) {
          toast?.call('Failed to add "$childLabel": $partialError');
        }
      } else {
        toast?.call('Drill down failed for $childLabel: $e');
      }
    }
  }

  Future<void> drillDownAllChildren() async {
    if (childrenWithMeta.isEmpty) {
      toast?.call('No children to drill down into');
      return;
    }

    toast?.call('Starting automatic drill down...');

    // For each child with an ID, try to clone a subtree from existing parents
    int clonedCount = 0;
    for (final child in childrenWithMeta) {
      final childLabel = child['label'] as String? ?? '';
      final childId = child['id'] as int?;

      if (childId == null) {
        toast?.call('Skipping "$childLabel" - no ID (please save changes first)');
        continue;
      }

      try {
        await tryCloneSubtreeForChildLabelAutomatic(childLabel);
        clonedCount++;
        // Wait a moment between clones to allow UI to update
        await Future.delayed(const Duration(milliseconds: 500));
      } catch (e) {
        toast?.call('Error cloning subtree for "$childLabel": $e');
      }
    }

    if (clonedCount == 0) {
      toast?.call('No children with IDs found - please save changes first');
    } else {
      toast?.call('Drill down completed - cloned $clonedCount subtrees');

      // Navigate to the first child to show the drilled down results
      if (childrenWithMeta.isNotEmpty) {
        final firstChild = childrenWithMeta.first;
        final firstChildId = firstChild['id'] as int?;
        final firstChildLabel = firstChild['label'] as String? ?? '';

        if (firstChildId != null) {
          await selectParent(firstChildId, firstChildLabel, currentDepth + 1);
          toast?.call('Navigated to $firstChildLabel to show drilled down children');
        }
      }
    }
  }


  bool canGoBack() => crumbs.length > 1;

  Future<void> goBack() async {
    if (crumbs.length <= 1) return;
    // pop current
    crumbs.removeLast();
    final prev = crumbs.last;
    await selectParent(prev['id'] as int, prev['label'] as String, prev['depth'] as int);
  }

  Future<void> deleteRoot(int rootId) async {
    isBusy = true; bannerError = null; notifyListeners();
    try {
      await repo.deleteRoot(rootId);
      await loadRoots();
    } catch (e) {
      bannerError = e.toString();
    } finally {
      isBusy = false; notifyListeners();
    }
  }

  // Jump to an ancestor crumb by node id:
  Future<void> jumpToCrumb(int nodeId) async {
    final idx = crumbs.indexWhere((c) => c['id'] == nodeId);
    if (idx == -1) return;
    // trim stack to selected
    while (crumbs.length > idx + 1) {
      crumbs.removeLast();
    }
    final c = crumbs.last;
    await selectParent(c['id'] as int, c['label'] as String, c['depth'] as int);
  }

  void setImportMode(String? mode) {
    if (mode == null || mode == importMode) {
      return;
    }
    importMode = mode;
    notifyListeners();
  }

  Future<void> importBytes(String mode, Uint8List bytes, String filename) async {
    importing = true;
    importMode = mode;
    importStatus = null;
    notifyListeners();
    try {
      final res = await repo.importFile(importMode, bytes, filename);
      final rows = res['rows'] ?? res['count'] ?? '?';
      final m = (res['mode'] ?? importMode).toString();
      importStatus = 'Imported $rows rows ($m)';
      await loadRoots(); // refresh left list
    } catch (e) {
      // Try to extract hint from error response if available
      String errorMsg = 'Import error: $e';
      final errorStr = e.toString();
      if (errorStr.contains('import failed:') && errorStr.contains('422')) {
        // Try to parse the 422 response for hint
        try {
          final parts = errorStr.split('422 ');
          if (parts.length > 1) {
            final responseBody = parts[1];
            // Simple hint extraction - look for "hint" in the response
            if (responseBody.contains('"hint"')) {
              errorMsg += '\n\nTip: Use headers like "Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions"';
            }
          }
        } catch (_) {
          // Ignore parsing errors, use basic message
        }
      }
      importStatus = errorMsg;
    } finally {
      importing = false;
      notifyListeners();
    }
  }

  // New feature methods
  Future<void> toggleRedFilter() async {
    filterOnlyRed = !filterOnlyRed;
    await reloadChildren();
  }

  Future<void> toggleEdgeFlag(int childId, bool currentRed) async {
    await repo.setEdgeFlag(currentParentId!, childId, !currentRed);
    await reloadChildren();
  }

  Future<String?> nextUnderfilled() async {
    if (crumbs.isEmpty) {
      return 'Select a root first';
    }
    final rootId = crumbs.first['id'] as int;
    final afterId = currentParentId;
    final res = await repo.nextUnderfilled(rootId: rootId, afterId: afterId);
    if (res == null) {
      return 'All parents under this root have ≥ 5 children';
    }
    if (!res.containsKey('id')) {
      return 'All parents under this root have ≥ 5 children';
    }
    final int id = res['id'] as int;
    final String label = (res['label'] as String?) ?? '';
    final int depth = (res['depth'] as int?) ?? 0;
    await selectParent(id, label, depth);
    // Refresh canonical crumbs from server-provided ancestors
    final a = await repo.ancestors(id);
    crumbs.clear();
    crumbs.addAll(a); // replace entirely
    notifyListeners();
    return null; // Successfully navigated, no error message
  }

  Future<void> tryCloneSubtreeForChildLabelAutomatic(String label) async {
    final items = await repo.findCloneCandidates(label);
    if (items.isEmpty) {
      toast?.call('No subtrees found for "$label"');
      return;
    }

    // Find the child ID that matches the label
    final child = childrenWithMeta.firstWhere(
      (c) => c['label'] == label,
      orElse: () => <String, dynamic>{},
    );

    if (child.isEmpty || child['id'] == null) {
      toast?.call('Child "$label" not found or has no ID');
      return;
    }

    final destChildId = child['id'] as int;

    // Automatically select the first candidate for drill down
    final selectedItem = items.first;

    final srcId = selectedItem['id'] as int?;
    if (srcId == null) {
      toast?.call('Invalid source ID for clone operation');
      return;
    }

    try {
      await repo.cloneSubtree(sourceId: srcId, destParentId: destChildId);
      toast?.call('Subtree cloned successfully for "$label"');
      await reloadChildren();
    } catch (e) {
      final errorMsg = e.toString();
      if (errorMsg.contains('max_children_exceeded') || errorMsg.contains('destination parent already has 5 children')) {
        toast?.call('Cannot clone: destination parent already has 5 children');
      } else if (errorMsg.contains('depth_limit_exceeded') || errorMsg.contains('cloned subtree would exceed depth limit')) {
        toast?.call('Cannot clone: subtree would exceed depth limit');
      } else {
        toast?.call('Clone failed: ${e.toString()}');
      }
    }
  }

  Future<void> tryCloneSubtreeForChildLabel(String label) async {
    final items = await repo.findCloneCandidates(label);
    if (items.isEmpty) {
      toast?.call('No subtrees found for "$label"');
      return;
    }

    final dest = currentParentId!;

    // If multiple candidates, show selection dialog
    Map<String, dynamic>? selectedItem;
    if (items.length == 1) {
      selectedItem = items.first;
    } else {
      // For now, just use the first item if multiple exist
      selectedItem = items.first;
      toast?.call('Multiple parents found for "$label", using first one');
    }

    final srcId = selectedItem['id'] as int?;
    if (srcId == null) {
      toast?.call('Invalid source ID for clone operation');
      return;
    }

    try {
      await repo.cloneSubtree(sourceId: srcId, destParentId: dest);
      toast?.call('Subtree cloned successfully for "$label"');
      await reloadChildren();
    } catch (e) {
      final errorMsg = e.toString();
      if (errorMsg.contains('max_children_exceeded') || errorMsg.contains('destination parent already has 5 children')) {
        toast?.call('Cannot clone: destination parent already has 5 children');
      } else if (errorMsg.contains('depth_limit_exceeded') || errorMsg.contains('cloned subtree would exceed depth limit')) {
        toast?.call('Cannot clone: subtree would exceed depth limit');
      } else {
        toast?.call('Clone failed: ${e.toString()}');
      }
    }
  }

  Future<void> exportCurrentRoot() async {
    if (crumbs.isEmpty) {
      toast?.call('Select a root first');
      return;
    }
    exporting = true;
    notifyListeners();
    try {
      final rootId = crumbs.first['id'] as int;
      final savedPath = await repo.exportCsv(rootId: rootId);
      if (savedPath != null) {
        toast?.call('Export saved: $savedPath');
      }
    } catch (e) {
      toast?.call('Export failed: $e');
    } finally {
      exporting = false;
      notifyListeners();
    }
  }

  Future<void> addRoot(String label) async {
    try {
      final created = await repo.createRoot(label);
      await loadRoots(); // refresh left list
      await selectParent(created['id'] as int, created['label'] as String, created['depth'] as int);
      toast?.call('Root created');
    } catch (e) {
      toast?.call('Create root failed: $e');
    }
  }

  Future<void> removeCurrentRootWithConfirm(BuildContext context) async {
    if (crumbs.isEmpty) {
      toast?.call('Select a root first');
      return;
    }
    final rootId = crumbs.first['id'] as int;
    final rootLabel = crumbs.first['label'] as String;

    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Root'),
        content: Text('Delete root "$rootLabel" and all its descendants?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Delete')),
        ],
      ),
    ) ?? false;

    if (!ok) return;

    try {
      await repo.deleteRoot(rootId);
      await loadRoots();
      // Select first available root if any
      if (roots.isNotEmpty) {
        final r = roots.first;
        await selectParent(r['id'] as int, r['label'] as String, r['depth'] as int);
      } else {
        crumbs.clear();
        currentParentId = null;
        childrenWithMeta = [];
        notifyListeners();
      }
      toast?.call('Root deleted');
    } catch (e) {
      toast?.call('Delete failed: $e');
    }
  }

  Future<void> onImportPreview(Uint8List bytes) async {
    isBusy = true; bannerError = null; notifyListeners();
    try {
      final res = await repo.importPreview(bytes);
      final errs = (res['errors'] as List?) ?? const [];
      if (errs.isNotEmpty) {
        bannerError = 'Import preview found ${errs.length} issue(s). Fix before applying.';
      } else {
        toast?.call('Preview OK: ${res['stats']?['found_paths'] ?? 0} paths');
      }
    } catch (e) {
      bannerError = e.toString();
    } finally {
      isBusy = false; notifyListeners();
    }
  }

  Future<void> onImportApply(Uint8List bytes) async {
    isBusy = true; bannerError = null; notifyListeners();
    try {
      await repo.importApply(bytes, enforceFive: true);
      toast?.call('Import completed');
      await loadRoots();
    } catch (e) {
      bannerError = e.toString();
    } finally {
      isBusy = false; notifyListeners();
    }
  }

  Future<void> goToNextIncomplete({int? rootId, int? afterId}) async {
    isBusy = true; bannerError = null; notifyListeners();
    try {
      final res = await repo.nextUnderfilled(rootId: rootId, afterId: afterId ?? currentParentId);
      if (res == null || !res.containsKey('id')) {
        toast?.call('All parents have ≤5 children');
        return;
      }
      final int id = res['id'] as int;
      final String label = (res['label'] as String?) ?? '';
      final int depth = (res['depth'] as int?) ?? 0;
      await selectParent(id, label, depth);
      final ancestors = await repo.ancestors(id);
      crumbs
        ..clear()
        ..addAll(ancestors);
      toast?.call('Jumped to next underfilled parent');
    } catch (e) {
      bannerError = e.toString();
    } finally {
      isBusy = false; notifyListeners();
    }
  }

  Future<void> deleteNodeWithUndo(int nodeId, {required int parentId}) async {
    try {
      isBusy = true; bannerError = null; notifyListeners();
      // 1) get snapshot
      final dry = await repo.deleteNodeDryRun(nodeId);
      final snap = (dry['snapshot'] as Map<String, dynamic>);
      // 2) apply delete
      await repo.deleteNodeApply(nodeId);
      // 3) stash snapshot for undo and refresh children
      lastDeleteSnapshot = snap;
      await reloadChildren();
    } catch (e) {
      bannerError = 'Delete failed: $e';
    } finally {
      isBusy = false; notifyListeners();
    }
  }

  Future<bool> undoLastDelete({required int parentId}) async {
    final snap = lastDeleteSnapshot;
    if (snap == null) return false;
    try {
      isBusy = true; bannerError = null; notifyListeners();
      await repo.restoreSubtree(snap);
      lastDeleteSnapshot = null;
      await reloadChildren();
      return true;
    } catch (e) {
      bannerError = 'Undo failed: $e';
      return false;
    } finally {
      isBusy = false; notifyListeners();
    }
  }

  /// Refreshes the entire VM Builder by reloading all data from the database
  Future<void> refreshAll() async {
    isBusy = true;
    bannerError = null;
    notifyListeners();

    try {
      // Reload roots to get fresh data from database
      await loadRoots();

      // If we have a current parent selected, reload its children too
      if (currentParentId != null) {
        await reloadChildren();
      }

      toast?.call('Database refreshed successfully');
    } catch (e) {
      bannerError = 'Refresh failed: $e';
      toast?.call('Refresh failed: $e');
    } finally {
      isBusy = false;
      notifyListeners();
    }
  }
}
