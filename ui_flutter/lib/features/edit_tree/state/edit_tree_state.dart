import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

class SlotState {
  final int slot;
  String text;
  String? error;
  String? warning;
  bool existing;

  SlotState(this.slot,
      {this.text = "", this.error, this.warning, this.existing = false});

  SlotState copyWith(
          {String? text, String? error, String? warning, bool? existing}) =>
      SlotState(
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
  final EditBanner? banner;

  EditTreeState({
    this.parentId,
    this.parentLabel = "",
    this.depth = 0,
    this.missingSlots = "",
    required this.slots,
    this.dirty = false,
    this.saving = false,
    this.banner,
  });

  EditTreeState copyWith({
    int? parentId,
    String? parentLabel,
    int? depth,
    String? missingSlots,
    List<SlotState>? slots,
    bool? dirty,
    bool? saving,
    EditBanner? banner,
  }) =>
      EditTreeState(
        parentId: parentId ?? this.parentId,
        parentLabel: parentLabel ?? this.parentLabel,
        depth: depth ?? this.depth,
        missingSlots: missingSlots ?? this.missingSlots,
        slots: slots ?? this.slots,
        dirty: dirty ?? this.dirty,
        saving: saving ?? this.saving,
        banner: banner ?? this.banner,
      );

  static EditTreeState empty() =>
      EditTreeState(slots: List.generate(5, (i) => SlotState(i + 1)));
}

class EditBanner {
  final String message;
  final String actionLabel;
  final VoidCallback? action;

  const EditBanner({
    required this.message,
    required this.actionLabel,
    this.action,
  });

  factory EditBanner.conflict({int? slot, VoidCallback? action}) {
    final slotMsg = slot != null ? ' in slot $slot' : '';
    return EditBanner(
      message: 'Concurrent changes detected$slotMsg. Your input is preserved.',
      actionLabel: 'Reload Latest',
      action: action,
    );
  }
}
