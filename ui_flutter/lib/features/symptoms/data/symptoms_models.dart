import 'package:freezed_annotation/freezed_annotation.dart';

part 'symptoms_models.freezed.dart';
part 'symptoms_models.g.dart';

@freezed
class IncompleteParent with _$IncompleteParent {
  const factory IncompleteParent({
    required int parentId,
    required String label,
    required int depth,
    required List<int> missingSlots,
    required String path,
    required DateTime updatedAt,
  }) = _IncompleteParent;

  factory IncompleteParent.fromJson(Map<String, dynamic> json) =>
      _$IncompleteParentFromJson(json);
}

@freezed
class ChildSlot with _$ChildSlot {
  const factory ChildSlot({
    required int slot,
    String? label,
    int? nodeId,
    bool? existing,
    String? error,
    String? warning,
  }) = _ChildSlot;

  factory ChildSlot.fromJson(Map<String, dynamic> json) =>
      _$ChildSlotFromJson(json);
}

@freezed
class ParentChildren with _$ParentChildren {
  const factory ParentChildren({
    required int parentId,
    required String parentLabel,
    required int depth,
    required String path,
    required List<ChildSlot> children,
    required List<int> missingSlots,
    String? version,
    String? etag,
  }) = _ParentChildren;

  factory ParentChildren.fromJson(Map<String, dynamic> json) =>
      _$ParentChildrenFromJson(json);
}

@freezed
class BatchAddRequest with _$BatchAddRequest {
  const factory BatchAddRequest({
    required List<String> labels,
    bool? replaceExisting,
  }) = _BatchAddRequest;

  factory BatchAddRequest.fromJson(Map<String, dynamic> json) =>
      _$BatchAddRequestFromJson(json);
}

@freezed
class DictionarySuggestion with _$DictionarySuggestion {
  const factory DictionarySuggestion({
    required int id,
    required String term,
    required String normalized,
    String? hints,
    bool? isRedFlag,
  }) = _DictionarySuggestion;

  factory DictionarySuggestion.fromJson(Map<String, dynamic> json) =>
      _$DictionarySuggestionFromJson(json);
}

@freezed
class ParentStatus with _$ParentStatus {
  const factory ParentStatus({
    required String status,
    String? message,
    int? filledCount,
    int? totalCount,
  }) = _ParentStatus;

  factory ParentStatus.fromJson(Map<String, dynamic> json) =>
      _$ParentStatusFromJson(json);
}

@freezed
class ChildrenUpdateIn with _$ChildrenUpdateIn {
  const factory ChildrenUpdateIn({
    String? version,
    required List<ChildSlot> children,
  }) = _ChildrenUpdateIn;

  factory ChildrenUpdateIn.fromJson(Map<String, dynamic> json) =>
      _$ChildrenUpdateInFromJson(json);
}

@freezed
class ChildrenUpdateOut with _$ChildrenUpdateOut {
  const factory ChildrenUpdateOut({
    required int parentId,
    required int version,
    required List<int> missingSlots,
    required List<int> updated,
  }) = _ChildrenUpdateOut;

  factory ChildrenUpdateOut.fromJson(Map<String, dynamic> json) =>
      _$ChildrenUpdateOutFromJson(json);
}

@freezed
class MaterializationResult with _$MaterializationResult {
  const factory MaterializationResult({
    required int added,
    required int filled,
    required int pruned,
    required int kept,
    String? log,
    DateTime? timestamp,
    List<String>? details,
  }) = _MaterializationResult;

  factory MaterializationResult.fromJson(Map<String, dynamic> json) =>
      _$MaterializationResultFromJson(json);
}

@freezed
class MaterializationHistoryItem with _$MaterializationHistoryItem {
  const factory MaterializationHistoryItem({
    required int id,
    required DateTime timestamp,
    required String operation,
    required MaterializationResult result,
    List<int>? parentIds,
    String? description,
  }) = _MaterializationHistoryItem;

  factory MaterializationHistoryItem.fromJson(Map<String, dynamic> json) =>
      _$MaterializationHistoryItemFromJson(json);
}

@freezed
class MaterializationPreview with _$MaterializationPreview {
  const factory MaterializationPreview({
    required int parentId,
    required List<String> willAdd,
    required List<String> willFill,
    required List<String> willPrune,
    required List<String> willKeep,
    String? warnings,
    bool? canUndo,
  }) = _MaterializationPreview;

  factory MaterializationPreview.fromJson(Map<String, dynamic> json) =>
      _$MaterializationPreviewFromJson(json);
}

@freezed
class MaterializationStats with _$MaterializationStats {
  const factory MaterializationStats({
    required int totalMaterializations,
    required int totalAdded,
    required int totalFilled,
    required int totalPruned,
    required int totalKept,
    DateTime? lastMaterialization,
    Map<String, int>? byOperationType,
  }) = _MaterializationStats;

  factory MaterializationStats.fromJson(Map<String, dynamic> json) =>
      _$MaterializationStatsFromJson(json);
}

enum SortMode {
  @JsonValue('issues_first')
  issuesFirst,
  @JsonValue('alphabetical')
  alphabetical,
  @JsonValue('recent_first')
  recentFirst,
}

enum ParentStatusType {
  @JsonValue('no_group')
  noGroup,
  @JsonValue('symptom_left_out')
  symptomLeftOut,
  @JsonValue('ok')
  ok,
  @JsonValue('overspecified')
  overspecified,
}
