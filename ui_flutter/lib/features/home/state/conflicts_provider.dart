import 'package:flutter/foundation.dart';
import '../data/conflicts_repo.dart';

class ConflictsState extends ChangeNotifier {
  final ConflictsRepo repo;
  
  ConflictsState(this.repo);

  bool isBusy = false;
  String? error;

  List<Map<String, dynamic>> items = [];
  Map<String, dynamic>? selectedConflict;
  final List<String> unionSelected = [];

  Future<void> scan() async {
    isBusy = true;
    error = null;
    notifyListeners();
    
    try {
      items = await repo.scan();
    } catch (e) {
      error = e.toString();
    } finally {
      isBusy = false;
      notifyListeners();
    }
  }

  void selectConflict(int idx) {
    selectedConflict = items[idx];
    unionSelected.clear();
    // Pre-select all children from the first occurrence as a starting point
    if (selectedConflict != null && selectedConflict!['parents'] is List) {
      final parents = selectedConflict!['parents'] as List;
      if (parents.isNotEmpty && parents[0]['children'] is List) {
        final firstChildren = List<String>.from(parents[0]['children'] as List);
        unionSelected.addAll(firstChildren.take(5)); // Max 5
      }
    }
    notifyListeners();
  }

  void toggleUnionChild(String label) {
    if (unionSelected.contains(label)) {
      unionSelected.remove(label);
    } else {
      if (unionSelected.length >= 5) return; // Block selection >5
      unionSelected.add(label);
    }
    notifyListeners();
  }

  Future<Map<String, dynamic>?> dryRun() async {
    final conflict = selectedConflict;
    if (conflict == null) return null;
    
    isBusy = true;
    error = null;
    notifyListeners();
    
    try {
      return await repo.resolve(
        label: conflict['label'] as String,
        selected: List<String>.from(unionSelected),
        dryRun: true,
      );
    } catch (e) {
      error = e.toString();
      return null;
    } finally {
      isBusy = false;
      notifyListeners();
    }
  }

  Future<Map<String, dynamic>?> apply() async {
    final conflict = selectedConflict;
    if (conflict == null) return null;
    
    isBusy = true;
    error = null;
    notifyListeners();
    
    try {
      final result = await repo.resolve(
        label: conflict['label'] as String,
        selected: List<String>.from(unionSelected),
        dryRun: false,
      );
      
      // Refresh conflicts list after successful apply
      await scan();
      return result;
    } catch (e) {
      error = e.toString();
      return null;
    } finally {
      isBusy = false;
      notifyListeners();
    }
  }

  void clearError() {
    error = null;
    notifyListeners();
  }
}
