import 'package:flutter/foundation.dart';

class SlotState {
  final int slot;
  String text;
  String? error;
  String? warning;
  bool existing;

  SlotState(this.slot, {this.text = "", this.error, this.warning, this.existing = false});

  SlotState copyWith({String? text, String? error, String? warning, bool? existing}) => SlotState(
        slot,
        text: text ?? this.text,
        error: error ?? this.error,
        warning: warning ?? this.warning,
        existing: existing ?? this.existing,
      );
}

class EditTreeState {
  final int? parentId;
  final String parentLabel;
  final int depth;
  final String missingSlots;
  final List<SlotState> slots;
  final bool dirty;
  final bool saving;

  EditTreeState({
    this.parentId,
    this.parentLabel = "",
    this.depth = 0,
    this.missingSlots = "",
    required this.slots,
    this.dirty = false,
    this.saving = false,
  });

  EditTreeState copyWith({
    int? parentId,
    String? parentLabel,
    int? depth,
    String? missingSlots,
    List<SlotState>? slots,
    bool? dirty,
    bool? saving,
  }) =>
      EditTreeState(
        parentId: parentId ?? this.parentId,
        parentLabel: parentLabel ?? this.parentLabel,
        depth: depth ?? this.depth,
        missingSlots: missingSlots ?? this.missingSlots,
        slots: slots ?? this.slots,
        dirty: dirty ?? this.dirty,
        saving: saving ?? this.saving,
      );

  static EditTreeState empty() =>
      EditTreeState(slots: List.generate(5, (i) => SlotState(i + 1)));
}
