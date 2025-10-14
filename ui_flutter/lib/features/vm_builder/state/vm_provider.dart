import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'dart:typed_data';
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
    if (currentParentId == null) return;
    loading = true;
    notifyListeners();
    try {
      // Get current server children to compare with local state
      final serverChildren = await repo.getChildren(currentParentId!);
      final serverLabels = serverChildren.map((c) => c['label'] as String).toList();

      // Check if we only have new children added (not modifications to existing ones)
      final onlyNewChildren = _onlyNewChildrenAdded(children, serverLabels);

      if (onlyNewChildren) {
        // Safe case: only adding new children, use the safe addChild method
        final newChildren = children.skip(serverLabels.length).toList();
        for (final childLabel in newChildren) {
          await repo.addChild(currentParentId!, childLabel);
        }
        toast?.call('${newChildren.length} child(ren) added successfully');
      } else if (_listsEqual(children, serverLabels)) {
        // No changes needed
        toast?.call('No changes to save');
      } else {
        // Unsafe case: modifications detected, warn user
        toast?.call('WARNING: This will replace all children. Existing child data may be lost.');
        // For now, don't save automatically - let user decide
        loading = false;
        notifyListeners();
        return;
      }

      // Reload children after save to get fresh server data with IDs
      await reloadChildren();
    } catch (e) {
      toast?.call('Save failed: $e');
    }
    loading = false;
    notifyListeners();
  }

  bool _onlyNewChildrenAdded(List<String> local, List<String> server) {
    // Check if local children are just server children + new ones at the end
    if (local.length <= server.length) return false;

    for (int i = 0; i < server.length; i++) {
      if (local[i] != server[i]) return false;
    }
    return true;
  }

  bool _listsEqual(List<String> a, List<String> b) {
    if (a.length != b.length) return false;
    for (int i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }

  Future<void> drillIntoChildByIndex(int index) async {
    if (index < 0 || index >= children.length) return;

    // Check if this index corresponds to an unsaved child
    final serverChildren = await repo.getChildren(currentParentId!);
    final isUnsavedChild = index >= serverChildren.length;

    if (isUnsavedChild) {
      // For unsaved children, show a message that they need to be saved first
      toast?.call('Please save changes before drilling into new children');
      return;
    }

    // For existing children, proceed with normal drill logic
    final child = serverChildren[index];
    final childId = child['id'] as int?;
    final childLabel = child['label'] as String;

    if (childId == null) {
      toast?.call('Child has no ID - this should not happen');
      return;
    }

    await selectParent(childId, childLabel, currentDepth + 1);
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

  Future<void> tryCloneSubtreeForChildLabel(String label) async {
    final items = await repo.findCloneCandidates(label);
    if (items.isEmpty) {
      // Show toast message - we'll need to implement this
      return;
    }
    // if 1 item, use it; else prompt simple dialog to pick
    final srcId = items.first['id'] as int;
    final dest = currentParentId!;
    final res = await repo.cloneSubtree(sourceId: srcId, destParentId: dest);
    // Show toast message - we'll need to implement this
    await reloadChildren();
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
}
