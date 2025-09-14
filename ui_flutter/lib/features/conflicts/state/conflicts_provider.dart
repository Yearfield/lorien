import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../../../core/http/api_client.dart';
import '../data/conflicts_repository.dart';

/// Provider for conflicts repository
final conflictsRepositoryProvider = Provider<ConflictsRepository>((ref) {
  final dio = ref.read(dioProvider);
  return ConflictsRepository(dio);
});

/// State for conflicts list
class ConflictsListState {
  final List<ConflictItem> items;
  final int total;
  final int? totalConflictsInitial;
  final int currentCount;
  final bool loading;
  final String? error;

  const ConflictsListState({
    this.items = const [],
    this.total = 0,
    this.totalConflictsInitial,
    this.currentCount = 0,
    this.loading = false,
    this.error,
  });

  ConflictsListState copyWith({
    List<ConflictItem>? items,
    int? total,
    int? totalConflictsInitial,
    int? currentCount,
    bool? loading,
    String? error,
  }) {
    return ConflictsListState(
      items: items ?? this.items,
      total: total ?? this.total,
      totalConflictsInitial: totalConflictsInitial ?? this.totalConflictsInitial,
      currentCount: currentCount ?? this.currentCount,
      loading: loading ?? this.loading,
      error: error,
    );
  }

  int get resolvedCount {
    final total = totalConflictsInitial ?? currentCount;
    return (total - currentCount).clamp(0, total);
  }

  double get progress {
    final total = totalConflictsInitial ?? currentCount;
    return total == 0 ? 1.0 : resolvedCount / total;
  }
}

/// State for selected group
class ConflictsGroupState {
  final int? selectedGroupNodeId;
  final List<ChildItem> childrenLabels;
  final Set<String> selectedLabels;
  final String? inlineNewLabel;
  final bool loading;
  final String? error;

  const ConflictsGroupState({
    this.selectedGroupNodeId,
    this.childrenLabels = const [],
    this.selectedLabels = const {},
    this.inlineNewLabel,
    this.loading = false,
    this.error,
  });

  ConflictsGroupState copyWith({
    int? selectedGroupNodeId,
    List<ChildItem>? childrenLabels,
    Set<String>? selectedLabels,
    String? inlineNewLabel,
    bool? loading,
    String? error,
  }) {
    return ConflictsGroupState(
      selectedGroupNodeId: selectedGroupNodeId ?? this.selectedGroupNodeId,
      childrenLabels: childrenLabels ?? this.childrenLabels,
      selectedLabels: selectedLabels ?? this.selectedLabels,
      inlineNewLabel: inlineNewLabel ?? this.inlineNewLabel,
      loading: loading ?? this.loading,
      error: error,
    );
  }

  bool get canAddInlineLabel => selectedLabels.length < 5;
  bool get canConfirm => selectedLabels.length == 5;
}

/// Notifier for conflicts list
class ConflictsListNotifier extends StateNotifier<ConflictsListState> {
  final ConflictsRepository _repository;

  ConflictsListNotifier(this._repository) : super(const ConflictsListState());

  Future<void> loadConflicts({int limit = 25, int offset = 0}) async {
    state = state.copyWith(loading: true, error: null);
    
    try {
      final page = await _repository.listConflicts(
        limit: limit, 
        offset: offset,
        onlyExactFive: true,
        onlyDuplicateParents: true,
        requireVariantSets: true,
      );
      
      // Capture initial total on first load
      final totalConflictsInitial = state.totalConflictsInitial ?? page.total;
      
      state = state.copyWith(
        loading: false,
        items: page.items,
        total: page.total,
        totalConflictsInitial: totalConflictsInitial,
        currentCount: page.items.length,
      );
    } catch (e) {
      state = state.copyWith(
        loading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> refresh() async {
    await loadConflicts();
  }
}

/// Notifier for conflicts group
class ConflictsGroupNotifier extends StateNotifier<ConflictsGroupState> {
  final ConflictsRepository _repository;
  final ConflictsListNotifier _listNotifier;

  ConflictsGroupNotifier(this._repository, this._listNotifier) : super(const ConflictsGroupState());

  Future<void> selectGroup(int nodeId) async {
    state = state.copyWith(
      loading: true,
      error: null,
      selectedGroupNodeId: nodeId,
    );

    try {
      final group = await _repository.loadGroup(nodeId);
      state = state.copyWith(
        loading: false,
        childrenLabels: group.children,
        selectedLabels: {},
        inlineNewLabel: null,
      );
    } catch (e) {
      state = state.copyWith(
        loading: false,
        error: e.toString(),
      );
    }
  }

  void toggleLabel(String label) {
    final newSelected = Set<String>.from(state.selectedLabels);
    
    if (newSelected.contains(label)) {
      newSelected.remove(label);  // Allow untick
    } else {
      if (newSelected.length >= 5) return;  // Guard max 5
      newSelected.add(label);
    }
    
    state = state.copyWith(selectedLabels: newSelected);
  }

  void setInlineNewLabel(String value) {
    state = state.copyWith(inlineNewLabel: value);
  }

  void addInlineLabel() {
    final label = state.inlineNewLabel?.trim();
    if (label == null || label.isEmpty) return;
    
    // Check for duplicates
    final existingLabels = state.childrenLabels.map((c) => c.label).toSet();
    if (existingLabels.contains(label) || state.selectedLabels.contains(label)) {
      return; // Duplicate, don't add
    }
    
    // Add to children labels (synthetic)
    final newChildren = List<ChildItem>.from(state.childrenLabels);
    newChildren.add(ChildItem(
      childId: -1, // Synthetic ID
      fromId: -1,
      slot: -1,
      label: label,
    ));
    
    // Auto-select if we have room
    final newSelected = Set<String>.from(state.selectedLabels);
    if (newSelected.length < 5) {
      newSelected.add(label);
    }
    
    state = state.copyWith(
      childrenLabels: newChildren,
      selectedLabels: newSelected,
      inlineNewLabel: null,
    );
  }

  Future<void> resolveGroup() async {
    if (!state.canConfirm) return;
    
    final groupId = state.selectedGroupNodeId;
    if (groupId == null) return;
    
    state = state.copyWith(loading: true, error: null);
    
    try {
      await _repository.resolveGroup(
        keepId: groupId,
        chosen: state.selectedLabels.toList(),
      );
      
      // Clear state after successful resolve
      state = const ConflictsGroupState();
      
      // Refresh the conflicts list to update progress
      await _listNotifier.refresh();
    } catch (e) {
      state = state.copyWith(
        loading: false,
        error: e.toString(),
      );
    }
  }

  void clearGroup() {
    state = const ConflictsGroupState();
  }
}

/// Providers
final conflictsListProvider = StateNotifierProvider<ConflictsListNotifier, ConflictsListState>((ref) {
  final repository = ref.read(conflictsRepositoryProvider);
  return ConflictsListNotifier(repository);
});

final conflictsGroupProvider = StateNotifierProvider<ConflictsGroupNotifier, ConflictsGroupState>((ref) {
  final repository = ref.read(conflictsRepositoryProvider);
  final listNotifier = ref.read(conflictsListProvider.notifier);
  return ConflictsGroupNotifier(repository, listNotifier);
});
