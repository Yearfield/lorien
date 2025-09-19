import 'package:flutter/foundation.dart';
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

  Future<void> loadRoots() async {
    loading = true; 
    notifyListeners();
    try {
      roots = await repo.getRoots();
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
}
