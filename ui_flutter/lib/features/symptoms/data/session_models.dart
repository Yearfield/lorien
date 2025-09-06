import 'package:freezed_annotation/freezed_annotation.dart';

part 'session_models.freezed.dart';
part 'session_models.g.dart';

@freezed
class SessionContext with _$SessionContext {
  const factory SessionContext({
    required DateTime timestamp,
    required Map<String, dynamic> uiState,
    required Map<String, dynamic> filters,
    required List<String> recentSheets,
    String? lastEditedSheet,
    Map<String, dynamic>? userPreferences,
  }) = _SessionContext;

  factory SessionContext.fromJson(Map<String, dynamic> json) =>
      _$SessionContextFromJson(json);
}

@freezed
class WorkbookSnapshot with _$WorkbookSnapshot {
  const factory WorkbookSnapshot({
    required String name,
    required DateTime createdAt,
    required Map<String, dynamic> data,
    required List<SheetSnapshot> sheets,
    Map<String, dynamic>? metadata,
  }) = _WorkbookSnapshot;

  factory WorkbookSnapshot.fromJson(Map<String, dynamic> json) =>
      _$WorkbookSnapshotFromJson(json);
}

@freezed
class SheetSnapshot with _$SheetSnapshot {
  const factory SheetSnapshot({
    required String name,
    required DateTime lastModified,
    required Map<String, dynamic> treeData,
    required List<String> vitalMeasurements,
    Map<String, dynamic>? overrides,
  }) = _SheetSnapshot;

  factory SheetSnapshot.fromJson(Map<String, dynamic> json) =>
      _$SheetSnapshotFromJson(json);
}

@freezed
class CsvPreview with _$CsvPreview {
  const factory CsvPreview({
    required List<String> headers,
    required List<Map<String, String>> rows,
    required Map<String, String> normalizedHeaders,
    required List<String> validationErrors,
    required Map<String, List<String>> headerSuggestions,
    int? totalRows,
  }) = _CsvPreview;

  factory CsvPreview.fromJson(Map<String, dynamic> json) =>
      _$CsvPreviewFromJson(json);
}

@freezed
class CsvImportResult with _$CsvImportResult {
  const factory CsvImportResult({
    required bool success,
    required int rowsProcessed,
    required int rowsImported,
    required List<String> errors,
    required List<String> warnings,
    Map<String, dynamic>? summary,
  }) = _CsvImportResult;

  factory CsvImportResult.fromJson(Map<String, dynamic> json) =>
      _$CsvImportResultFromJson(json);
}

@freezed
class PushLogEntry with _$PushLogEntry {
  const factory PushLogEntry({
    required int id,
    required DateTime timestamp,
    required String operation,
    required String description,
    Map<String, dynamic>? metadata,
    String? user,
    bool? success,
  }) = _PushLogEntry;

  factory PushLogEntry.fromJson(Map<String, dynamic> json) =>
      _$PushLogEntryFromJson(json);
}

@freezed
class PushLogSummary with _$PushLogSummary {
  const factory PushLogSummary({
    required List<PushLogEntry> entries,
    required int totalEntries,
    DateTime? lastSync,
    Map<String, int>? operationsByType,
  }) = _PushLogSummary;

  factory PushLogSummary.fromJson(Map<String, dynamic> json) =>
      _$PushLogSummaryFromJson(json);
}

@freezed
class SessionExport with _$SessionExport {
  const factory SessionExport({
    required String version,
    required DateTime exportedAt,
    required SessionContext context,
    required WorkbookSnapshot workbook,
    Map<String, dynamic>? settings,
  }) = _SessionExport;

  factory SessionExport.fromJson(Map<String, dynamic> json) =>
      _$SessionExportFromJson(json);
}

@freezed
class SessionImportResult with _$SessionImportResult {
  const factory SessionImportResult({
    required bool success,
    required List<String> importedSheets,
    required List<String> errors,
    required List<String> warnings,
    Map<String, dynamic>? conflicts,
  }) = _SessionImportResult;

  factory SessionImportResult.fromJson(Map<String, dynamic> json) =>
      _$SessionImportResultFromJson(json);
}
