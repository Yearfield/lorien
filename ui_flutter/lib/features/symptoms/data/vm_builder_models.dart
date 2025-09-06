import 'package:freezed_annotation/freezed_annotation.dart';
import 'symptoms_models.dart';

part 'vm_builder_models.freezed.dart';
part 'vm_builder_models.g.dart';

@freezed
class VitalMeasurementDraft with _$VitalMeasurementDraft {
  const factory VitalMeasurementDraft({
    required String label,
    List<NodeDraft>? nodes,
    bool? isTemplate,
  }) = _VitalMeasurementDraft;

  factory VitalMeasurementDraft.fromJson(Map<String, dynamic> json) =>
      _$VitalMeasurementDraftFromJson(json);
}

@freezed
class NodeDraft with _$NodeDraft {
  const factory NodeDraft({
    required int depth,
    required int slot,
    required String label,
    List<NodeDraft>? children,
  }) = _NodeDraft;

  factory NodeDraft.fromJson(Map<String, dynamic> json) =>
      _$NodeDraftFromJson(json);
}

@freezed
class SheetDraft with _$SheetDraft {
  const factory SheetDraft({
    required String name,
    required List<VitalMeasurementDraft> vitalMeasurements,
    Map<String, dynamic>? metadata,
  }) = _SheetDraft;

  factory SheetDraft.fromJson(Map<String, dynamic> json) =>
      _$SheetDraftFromJson(json);
}

@freezed
class ValidationResult with _$ValidationResult {
  const factory ValidationResult({
    required bool isValid,
    List<String>? errors,
    List<String>? warnings,
    Map<String, dynamic>? suggestions,
  }) = _ValidationResult;

  factory ValidationResult.fromJson(Map<String, dynamic> json) =>
      _$ValidationResultFromJson(json);
}

@freezed
class CreationResult with _$CreationResult {
  const factory CreationResult({
    required bool success,
    List<int>? createdVmIds,
    List<int>? createdNodeIds,
    MaterializationResult? materializationResult,
    List<String>? errors,
  }) = _CreationResult;

  factory CreationResult.fromJson(Map<String, dynamic> json) =>
      _$CreationResultFromJson(json);
}

@freezed
class DuplicateCheckResult with _$DuplicateCheckResult {
  const factory DuplicateCheckResult({
    required bool hasDuplicates,
    List<String>? duplicateLabels,
    Map<String, List<String>>? conflicts,
  }) = _DuplicateCheckResult;

  factory DuplicateCheckResult.fromJson(Map<String, dynamic> json) =>
      _$DuplicateCheckResultFromJson(json);
}
