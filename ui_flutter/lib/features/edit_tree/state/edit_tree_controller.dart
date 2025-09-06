import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../../../api/lorien_api.dart';
import '../../../data/dto/child_slot_dto.dart';
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
    try {
      final data = await repo.getParentChildren(parentId);

      // Convert children to slot states
      final slots = List.generate(5, (i) {
        final slot = i + 1;
        final child = data.children.firstWhere(
          (c) => c.slot == slot,
          orElse: () => ChildInfo(0, '', slot, data.children.first.depth, false),
        );
        final text = child.label;
        final existing = child.id != 0;
        return SlotState(slot, text: text, existing: existing);
      });

      state = state.copyWith(
        parentId: parentId,
        parentLabel: label ?? data.path['vital_measurement'] ?? '',
        depth: depth ?? data.children.first.depth - 1,
        missingSlots: data.missingSlots.join(','),
        slots: slots,
        dirty: false,
      );

      _computeDuplicateWarnings();
    } catch (e) {
      // Handle error - could be network or API error
      state = state.copyWith(
        banner: EditBanner(
          message: 'Failed to load parent data: $e',
          actionLabel: 'Retry',
          action: () => loadParent(parentId, label: label, depth: depth, missing: missing),
        ),
      );
    }
  }

  void putSlot(int slot, String text) {
    final slots = state.slots.map((s) =>
        s.slot == slot ? s.copyWith(text: text, error: null, warning: null) : s).toList();
    state = state.copyWith(slots: slots, dirty: true);
    _computeDuplicateWarnings();
  }

  void _computeDuplicateWarnings() {
    final map = <String, List<int>>{};
    for (final s in state.slots) {
      final trimmed = s.text.trim().toLowerCase();
      if (trimmed.isNotEmpty) {
        map.putIfAbsent(trimmed, () => []).add(s.slot);
      }
    }

    final warnings = <int, String>{};
    map.forEach((label, slots) {
      if (slots.length > 1) {
        for (final slot in slots) {
          warnings[slot] = 'Duplicate label under same parent (will fail on save)';
        }
      }
    });

    final updatedSlots = state.slots.map((s) {
      final warning = warnings[s.slot];
      if (warning != null) {
        return s.copyWith(warning: warning);
      } else {
        return SlotState(s.slot, text: s.text, error: s.error, warning: null, existing: s.existing);
      }
    }).toList();

    state = state.copyWith(slots: updatedSlots);
  }

  Future<void> save() async {
    if (state.parentId == null) return;

    state = state.copyWith(saving: true);

    final slots = state.slots.map((s) => ChildSlotDTO(slot: s.slot, label: s.text)).toList();

    try {
      final res = await repo.updateParentChildren(state.parentId!, slots);

      // Update state with response
      final missingSlots = List<int>.from(res['missing_slots'] as List? ?? []);
      final updatedSlots = state.slots.map((s) {
        return s.copyWith(error: null, warning: null); // Clear errors on success
      }).toList();

      state = state.copyWith(
        missingSlots: missingSlots.join(','),
        slots: updatedSlots,
        dirty: false,
        saving: false,
        banner: null, // Clear any previous banner
      );
    } on DioException catch (e) {
      state = state.copyWith(saving: false);

      if (e.response?.statusCode == 409) {
        // Handle optimistic concurrency conflicts
        final details = LorienApi.extractDetailErrors(e);
        final banner = EditBanner.conflict(action: () => reloadLatest());
        state = state.copyWith(banner: banner);
      } else if (e.response?.statusCode == 422) {
        // Handle validation errors
        final details = LorienApi.extractDetailErrors(e);
        var slots = state.slots;

        for (final detail in details) {
          final ctx = detail['ctx'] as Map<String, dynamic>?;
          final msg = detail['msg'] as String? ?? 'Invalid';
          final slot = ctx?['slot'] as int?;

          if (slot != null) {
            slots = slots.map((s) =>
                s.slot == slot ? s.copyWith(error: msg) : s).toList();
          }
        }

        final banner = EditBanner(
          message: 'Validation errors found. Please fix the highlighted fields.',
          actionLabel: 'Dismiss',
          action: () => state = state.copyWith(banner: null),
        );
        state = state.copyWith(slots: slots, banner: banner);
      } else {
        // Handle other errors
        final banner = EditBanner(
          message: 'Save failed: ${e.message}',
          actionLabel: 'Retry',
          action: () => save(),
        );
        state = state.copyWith(banner: banner);
      }
    } catch (e) {
      state = state.copyWith(saving: false);
      final banner = EditBanner(
        message: 'Unexpected error: $e',
        actionLabel: 'Retry',
        action: () => save(),
      );
      state = state.copyWith(banner: banner);
    }
  }

  Future<void> reset() async {
    if (state.parentId != null) {
      await loadParent(state.parentId!);
    }
  }

  Future<void> reloadLatest() async {
    if (state.parentId == null) return;

    try {
      // Keep user's current input for ghost values
      final userInput = Map.fromEntries(
        state.slots.map((s) => MapEntry(s.slot, s.text))
      );

      // Reload fresh data from server
      await loadParent(state.parentId!);

      // Clear banner after successful reload
      state = state.copyWith(banner: null);

      // Optionally show ghost values or keep fresh server state
      // For now, we keep the fresh server state as the source of truth
    } catch (e) {
      // If reload fails, keep banner but update message
      final banner = EditBanner(
        message: 'Failed to reload latest data. Please try again.',
        actionLabel: 'Retry',
        action: () => reloadLatest(),
      );
      state = state.copyWith(banner: banner);
    }
  }
}
