import 'package:flutter/foundation.dart';
import 'dart:typed_data';
import '../data/vm_repo.dart';

class VmState extends ChangeNotifier {
  final VmRepo repo;
  VmState(this.repo);

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

  Future<void> loadRoots() async {
    loading = true; 
    notifyListeners();
    try {
      roots = await repo.getRoots();
      crumbs.clear();
      currentParentId = null; 
      currentParentLabel = null; 
      children = [];
    } catch (e) {
      // Handle error silently for now
      roots = [];
    }
    loading = false; 
    notifyListeners();
  }

  Future<void> selectParent(int id, String label, int depth) async {
    currentParentId = id;
    currentParentLabel = label;
    currentDepth = depth;
    // push crumb
    crumbs.removeWhere((e) => e['id'] == id);
    crumbs.add({'id': id, 'label': label, 'depth': depth});
    loading = true; 
    notifyListeners();
    try {
      final ch = await repo.getChildren(id);
      children = ch.map((e) => (e['label'] as String)).toList();
    } catch (e) {
      // Handle error silently for now
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
    await repo.deleteRoot(rootId);
    await loadRoots();
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
}
