import 'package:freezed_annotation/freezed_annotation.dart';

part 'conflicts_models.freezed.dart';
part 'conflicts_models.g.dart';

@freezed
class ConflictItem with _$ConflictItem {
  const factory ConflictItem({
    required int id,
    required ConflictType type,
    required String description,
    required List<int> affectedNodes,
    required List<String> affectedLabels,
    int? parentId,
    int? depth,
    String? resolution,
    DateTime? detectedAt,
  }) = _ConflictItem;

  factory ConflictItem.fromJson(Map<String, dynamic> json) =>
      _$ConflictItemFromJson(json);
}

@freezed
class ConflictGroup with _$ConflictGroup {
  const factory ConflictGroup({
    required ConflictType type,
    required List<ConflictItem> items,
    required int totalCount,
    String? summary,
  }) = _ConflictGroup;

  factory ConflictGroup.fromJson(Map<String, dynamic> json) =>
      _$ConflictGroupFromJson(json);
}

@freezed
class ConflictsReport with _$ConflictsReport {
  const factory ConflictsReport({
    required List<ConflictGroup> groups,
    required int totalConflicts,
    DateTime? generatedAt,
    Map<String, int>? byType,
  }) = _ConflictsReport;

  factory ConflictsReport.fromJson(Map<String, dynamic> json) =>
      _$ConflictsReportFromJson(json);
}

@freezed
class ConflictResolution with _$ConflictResolution {
  const factory ConflictResolution({
    required int conflictId,
    required String action,
    String? newValue,
    Map<String, dynamic>? metadata,
  }) = _ConflictResolution;

  factory ConflictResolution.fromJson(Map<String, dynamic> json) =>
      _$ConflictResolutionFromJson(json);
}

enum ConflictType {
  @JsonValue('duplicate_labels')
  duplicateLabels,
  @JsonValue('orphans')
  orphans,
  @JsonValue('depth_anomalies')
  depthAnomalies,
  @JsonValue('missing_slots')
  missingSlots,
  @JsonValue('invalid_references')
  invalidReferences,
}

enum ConflictSeverity {
  @JsonValue('low')
  low,
  @JsonValue('medium')
  medium,
  @JsonValue('high')
  high,
  @JsonValue('critical')
  critical,
}
