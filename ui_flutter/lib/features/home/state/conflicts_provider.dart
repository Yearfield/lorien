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
  final List<String> unionOptions = [];

  Future<void> scan() async {
    isBusy = true;
    error = null;
    notifyListeners();

    try {
      final previousLabel = _normalizeLabel(selectedConflict?["label"]);
      items = await repo.scan();

      if (previousLabel.isNotEmpty) {
        final idx = items.indexWhere(
          (item) => _normalizeLabel(item["label"]) == previousLabel,
        );

        if (idx != -1) {
          _hydrateSelection(items[idx]);
        } else {
          selectedConflict = null;
          unionSelected.clear();
          unionOptions.clear();
        }
      } else {
        selectedConflict = null;
        unionSelected.clear();
        unionOptions.clear();
      }
    } catch (e) {
      error = e.toString();
    } finally {
      isBusy = false;
      notifyListeners();
    }
  }

  void selectConflict(int idx) {
    _hydrateSelection(items[idx]);
    notifyListeners();
  }

  void toggleUnionChild(String label) {
    if (!unionOptions.contains(label)) {
      return;
    }

    if (unionSelected.contains(label)) {
      unionSelected.remove(label);
    } else {
      if (unionSelected.length >= 5) return; // Block selection >5
      unionSelected.add(label);
    }
    notifyListeners();
  }

  bool addUnionChild(String label) {
    final cleaned = label.trim();
    if (cleaned.isEmpty) {
      return false;
    }

    final normalized = _normalizeLabel(cleaned);
    final exists = unionOptions.any(
      (existing) => _normalizeLabel(existing) == normalized,
    );

    if (exists) {
      return false;
    }

    unionOptions.add(cleaned);
    if (unionSelected.length < 5) {
      unionSelected.add(cleaned);
    }

    notifyListeners();
    return true;
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

  void _hydrateSelection(Map<String, dynamic> conflict) {
    selectedConflict = conflict;

    unionOptions
      ..clear();
    if (conflict['union_children'] is List) {
      unionOptions.addAll(
        List<String>.from(conflict['union_children'] as List),
      );
    }

    unionSelected
      ..clear();

    // Pre-select all children from the first occurrence as a starting point
    if (conflict['parents'] is List) {
      final parents = conflict['parents'] as List;
      if (parents.isNotEmpty && parents[0]['children'] is List) {
        final firstChildren = List<String>.from(parents[0]['children'] as List);
        unionSelected.addAll(firstChildren.take(5));
      }
    }
  }

  String _normalizeLabel(Object? value) {
    if (value == null) {
      return '';
    }
    return value.toString().trim().toLowerCase();
  }
}
