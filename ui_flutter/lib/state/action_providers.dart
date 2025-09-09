import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/dto/child_slot_dto.dart';
import '../data/dto/triage_dto.dart';
import '../data/repos/tree_repository.dart';
import '../data/repos/triage_repository.dart';
import '../data/repos/flags_repository.dart';
import '../data/repos/calc_repository.dart';
import 'repository_providers.dart';

// Action State Classes
class ActionState<T> {
  final bool isLoading;
  final T? data;
  final String? error;

  const ActionState({
    this.isLoading = false,
    this.data,
    this.error,
  });

  ActionState<T> copyWith({
    bool? isLoading,
    T? data,
    String? error,
  }) {
    return ActionState<T>(
      isLoading: isLoading ?? this.isLoading,
      data: data ?? this.data,
      error: error ?? this.error,
    );
  }
}

// Tree Action Providers
final upsertChildrenProvider = StateNotifierProvider<UpsertChildrenNotifier,
    ActionState<Map<String, dynamic>>>((ref) {
  final repository = ref.watch(treeRepositoryProvider);
  return UpsertChildrenNotifier(repository);
});

class UpsertChildrenNotifier
    extends StateNotifier<ActionState<Map<String, dynamic>>> {
  final TreeRepository _repository;

  UpsertChildrenNotifier(this._repository) : super(const ActionState());

  Future<void> upsertChildren(int parentId, List<ChildSlotDTO> children) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final result = await _repository.upsertChildren(parentId, children);
      state = state.copyWith(isLoading: false, data: result);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void reset() {
    state = const ActionState();
  }
}

// Triage Action Providers
final updateTriageProvider =
    StateNotifierProvider<UpdateTriageNotifier, ActionState<void>>((ref) {
  final repository = ref.watch(triageRepositoryProvider);
  return UpdateTriageNotifier(repository);
});

class UpdateTriageNotifier extends StateNotifier<ActionState<void>> {
  final TriageRepository _repository;

  UpdateTriageNotifier(this._repository) : super(const ActionState());

  Future<void> updateTriage(int nodeId, TriageDTO triage) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      await _repository.updateTriage(nodeId, triage);
      state = state.copyWith(isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void reset() {
    state = const ActionState();
  }
}

// Flags Action Providers
final assignFlagProvider =
    StateNotifierProvider<AssignFlagNotifier, ActionState<void>>((ref) {
  final repository = ref.watch(flagsRepositoryProvider);
  return AssignFlagNotifier(repository);
});

class AssignFlagNotifier extends StateNotifier<ActionState<void>> {
  final FlagsRepository _repository;

  AssignFlagNotifier(this._repository) : super(const ActionState());

  Future<void> assignFlag(int nodeId, String redFlagName) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      await _repository.assignFlag(nodeId, redFlagName);
      state = state.copyWith(isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void reset() {
    state = const ActionState();
  }
}

// Calculator Action Providers
final exportCsvProvider =
    StateNotifierProvider<ExportCsvNotifier, ActionState<String>>((ref) {
  final repository = ref.watch(calcRepositoryProvider);
  return ExportCsvNotifier(repository);
});

class ExportCsvNotifier extends StateNotifier<ActionState<String>> {
  final CalcRepository _repository;

  ExportCsvNotifier(this._repository) : super(const ActionState());

  Future<void> exportCsv() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final csvData = await _repository.exportCsv();
      state = state.copyWith(isLoading: false, data: csvData);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void reset() {
    state = const ActionState();
  }
}
