import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../data/edit_tree_repository.dart';
import '../data/edit_tree_provider.dart';
import 'edit_tree_state.dart';

final editTreeControllerProvider =
    StateNotifierProvider.autoDispose<EditTreeController, EditTreeState>(
  (ref) {
    final repo = ref.watch(editTreeRepositoryProvider);
    return EditTreeController(repo);
  },
);

class EditTreeController extends StateNotifier<EditTreeState> {
  final EditTreeRepository repo;

  EditTreeController(this.repo) : super(EditTreeState.empty());

  Future<void> loadParent(
    int parentId, {
    String? label,
    int? depth,
    String? missing,
  }) async {
    final rows = await repo.getChildren(parentId);
    final slots = List.generate(5, (i) {
      final s = i + 1;
      final row = rows.firstWhere(
        (r) => r['slot'] == s,
        orElse: () => {},
      );
      final text = (row is Map && row['label'] != null)
          ? (row['label'] as String)
          : "";
      final existing = (row is Map && row['id'] != null);
      return SlotState(s, text: text, existing: existing);
    });

    state = state.copyWith(
      parentId: parentId,
      parentLabel: label ?? state.parentLabel,
      depth: depth ?? state.depth,
      missingSlots: missing ?? state.missingSlots,
      slots: slots,
      dirty: false,
    );
  }

  void putSlot(int slot, String text) {
    final slots = state.slots.map((s) =>
        s.slot == slot ? s.copyWith(text: text, error: null) : s).toList();
    state = state.copyWith(slots: slots, dirty: true);
  }

  Future<void> save() async {
    if (state.parentId == null) return;

    state = state.copyWith(saving: true);
    final patches = state.slots
        .map((s) => SlotPatch(s.slot, s.text))
        .toList();

    try {
      final res = await repo.upsertChildren(state.parentId!, patches);

      // Update existing flags & missing
      final updatedSlots = state.slots.map((s) {
        final hit = res.updated.firstWhere(
          (u) => u['slot'] == s.slot,
          orElse: () => {},
        );
        if (hit is Map && hit.isNotEmpty) {
          return s.copyWith(existing: true);
        }
        return s;
      }).toList();

      state = state.copyWith(
        missingSlots: res.missingSlots,
        slots: updatedSlots,
        dirty: false,
        saving: false,
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 409) {
        final slot = (e.response?.data is Map)
            ? (e.response?.data['slot'] as int?)
            : null;
        final slots = state.slots.map((s) =>
            s.slot == slot
                ? s.copyWith(error: "Concurrent edit on slot ${slot ?? ''}. Reload and retry.")
                : s).toList();
        state = state.copyWith(slots: slots, saving: false);
      } else if (e.response?.statusCode == 422) {
        final details = (e.response?.data?['detail'] as List?) ?? [];
        var slots = state.slots;
        for (final d in details) {
          final ctx = (d is Map) ? d['ctx'] as Map<String, dynamic>? : null;
          final msg = (d is Map) ? (d['msg'] as String? ?? "Invalid") : "Invalid";
          final slot = ctx?['slot'] as int?;
          if (slot != null) {
            slots = slots.map((s) =>
                s.slot == slot ? s.copyWith(error: msg) : s).toList();
          }
        }
        state = state.copyWith(slots: slots, saving: false);
      } else {
        state = state.copyWith(saving: false);
        rethrow;
      }
    }
  }

  Future<void> reset() async {
    if (state.parentId != null) {
      await loadParent(state.parentId!);
    }
  }
}
