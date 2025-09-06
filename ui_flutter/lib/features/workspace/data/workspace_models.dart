import 'package:freezed_annotation/freezed_annotation.dart';

part 'workspace_models.freezed.dart';
part 'workspace_models.g.dart';

@freezed
class ImportJob with _$ImportJob {
  const factory ImportJob({
    required String id,
    required String fileName,
    required String status,
    required DateTime startedAt,
    DateTime? completedAt,
    required int totalRows,
    required int processedRows,
    required int importedRows,
    List<String>? errors,
    List<String>? warnings,
    Map<String, dynamic>? headerMapping,
    Map<String, dynamic>? validationResults,
  }) = _ImportJob;

  factory ImportJob.fromJson(Map<String, dynamic> json) =>
      _$ImportJobFromJson(json);
}

@freezed
class BackupRestoreStatus with _$BackupRestoreStatus {
  const factory BackupRestoreStatus({
    required String operation,
    required String status,
    required DateTime startedAt,
    DateTime? completedAt,
    required int totalItems,
    required int processedItems,
    String? errorMessage,
    Map<String, dynamic>? details,
    bool? integrityCheckPassed,
  }) = _BackupRestoreStatus;

  factory BackupRestoreStatus.fromJson(Map<String, dynamic> json) =>
      _$BackupRestoreStatusFromJson(json);
}

@freezed
class HeaderValidationError with _$HeaderValidationError {
  const factory HeaderValidationError({
    required int row,
    required int colIndex,
    required String expected,
    required String received,
    String? suggestion,
  }) = _HeaderValidationError;

  factory HeaderValidationError.fromJson(Map<String, dynamic> json) =>
      _$HeaderValidationErrorFromJson(json);
}

@freezed
class ImportValidationResult with _$ImportValidationResult {
  const factory ImportValidationResult({
    required bool isValid,
    List<HeaderValidationError>? headerErrors,
    Map<String, int>? typeCounts,
    List<String>? generalErrors,
    Map<String, dynamic>? preview,
  }) = _ImportValidationResult;

  factory ImportValidationResult.fromJson(Map<String, dynamic> json) =>
      _$ImportValidationResultFromJson(json);
}

@freezed
class BackupMetadata with _$BackupMetadata {
  const factory BackupMetadata({
    required String version,
    required DateTime createdAt,
    required String checksum,
    required Map<String, int> recordCounts,
    Map<String, dynamic>? settings,
    String? description,
  }) = _BackupMetadata;

  factory BackupMetadata.fromJson(Map<String, dynamic> json) =>
      _$BackupMetadataFromJson(json);
}

enum ImportStatus {
  @JsonValue('queued')
  queued,
  @JsonValue('processing')
  processing,
  @JsonValue('completed')
  completed,
  @JsonValue('failed')
  failed,
  @JsonValue('cancelled')
  cancelled,
}

enum BackupStatus {
  @JsonValue('creating')
  creating,
  @JsonValue('validating')
  validating,
  @JsonValue('completed')
  completed,
  @JsonValue('failed')
  failed,
}
