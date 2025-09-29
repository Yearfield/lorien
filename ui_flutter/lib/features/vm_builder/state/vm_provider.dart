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
    children = [...children, label.trim()];
    notifyListeners();
  }

  void removeChildAt(int idx) {
    children = [...children]..removeAt(idx);
    notifyListeners();
  }

  Future<void> save() async {
    if (currentParentId == null) return;
    loading = true; 
    notifyListeners();
    try {
      await repo.putChildren(currentParentId!, children);
    } catch (e) {
      // Handle error silently for now
    }
    loading = false; 
    notifyListeners();
  }

  Future<void> drillIntoChildByIndex(int index) async {
    if (index < 0 || index >= children.length) return;
    // Resolve or create the child node by label (ensure it exists server-side)
    // We rely on putChildren to create by label only when saving; for drill, we need the id.
    // Fetch server children to read ids:
    final raw = await repo.getChildren(currentParentId!);
    final row = raw[index];
    final childId = row['id'] as int?;
    final childLabel = row['label'] as String;

    if (childId == null) {
      // safeguard: if no id, force a save first
      await save();
    }
    final latest = await repo.getChildren(currentParentId!);
    final child = latest[index];
    final id = child['id'] as int;
    await selectParent(id, childLabel, currentDepth + 1);
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

  Future<void> importBytes(String mode, Uint8List bytes, String filename) async {
    importing = true; 
    importStatus = null; 
    notifyListeners();
    try {
      final res = await repo.importFile(mode, bytes, filename);
      final rows = res['rows'] ?? res['count'] ?? '?';
      final m = (res['mode'] ?? mode).toString();
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
    await selectParent(res['id'] as int, res['label'] as String, res['depth'] as int);
    // Refresh canonical crumbs
    final a = await repo.ancestors(res['id'] as int);
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
      await repo.exportCsv(rootId: rootId);
      toast?.call('Export saved to Downloads');
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
      final res = await repo.nextUnderfilled(rootId: rootId, afterId: afterId);
      final parentId = res['parent_id'] as int?;
      if (parentId == null) {
        toast?.call('All parents have ≤5 children');
        return;
      }
      // client should navigate to parentId; for now just set it
      currentParentId = parentId;
      // downstream UI will call a method to load children for currentParentId
    } catch (e) {
      bannerError = e.toString();
    } finally {
      isBusy = false; notifyListeners();
    }
  }
}
