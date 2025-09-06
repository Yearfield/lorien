// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'session_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$SessionContextImpl _$$SessionContextImplFromJson(Map<String, dynamic> json) =>
    _$SessionContextImpl(
      timestamp: DateTime.parse(json['timestamp'] as String),
      uiState: json['uiState'] as Map<String, dynamic>,
      filters: json['filters'] as Map<String, dynamic>,
      recentSheets: (json['recentSheets'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      lastEditedSheet: json['lastEditedSheet'] as String?,
      userPreferences: json['userPreferences'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$SessionContextImplToJson(
        _$SessionContextImpl instance) =>
    <String, dynamic>{
      'timestamp': instance.timestamp.toIso8601String(),
      'uiState': instance.uiState,
      'filters': instance.filters,
      'recentSheets': instance.recentSheets,
      'lastEditedSheet': instance.lastEditedSheet,
      'userPreferences': instance.userPreferences,
    };

_$WorkbookSnapshotImpl _$$WorkbookSnapshotImplFromJson(
        Map<String, dynamic> json) =>
    _$WorkbookSnapshotImpl(
      name: json['name'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      data: json['data'] as Map<String, dynamic>,
      sheets: (json['sheets'] as List<dynamic>)
          .map((e) => SheetSnapshot.fromJson(e as Map<String, dynamic>))
          .toList(),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$WorkbookSnapshotImplToJson(
        _$WorkbookSnapshotImpl instance) =>
    <String, dynamic>{
      'name': instance.name,
      'createdAt': instance.createdAt.toIso8601String(),
      'data': instance.data,
      'sheets': instance.sheets,
      'metadata': instance.metadata,
    };

_$SheetSnapshotImpl _$$SheetSnapshotImplFromJson(Map<String, dynamic> json) =>
    _$SheetSnapshotImpl(
      name: json['name'] as String,
      lastModified: DateTime.parse(json['lastModified'] as String),
      treeData: json['treeData'] as Map<String, dynamic>,
      vitalMeasurements: (json['vitalMeasurements'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      overrides: json['overrides'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$SheetSnapshotImplToJson(_$SheetSnapshotImpl instance) =>
    <String, dynamic>{
      'name': instance.name,
      'lastModified': instance.lastModified.toIso8601String(),
      'treeData': instance.treeData,
      'vitalMeasurements': instance.vitalMeasurements,
      'overrides': instance.overrides,
    };

_$CsvPreviewImpl _$$CsvPreviewImplFromJson(Map<String, dynamic> json) =>
    _$CsvPreviewImpl(
      headers:
          (json['headers'] as List<dynamic>).map((e) => e as String).toList(),
      rows: (json['rows'] as List<dynamic>)
          .map((e) => Map<String, String>.from(e as Map))
          .toList(),
      normalizedHeaders:
          Map<String, String>.from(json['normalizedHeaders'] as Map),
      validationErrors: (json['validationErrors'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      headerSuggestions:
          (json['headerSuggestions'] as Map<String, dynamic>).map(
        (k, e) =>
            MapEntry(k, (e as List<dynamic>).map((e) => e as String).toList()),
      ),
      totalRows: (json['totalRows'] as num?)?.toInt(),
    );

Map<String, dynamic> _$$CsvPreviewImplToJson(_$CsvPreviewImpl instance) =>
    <String, dynamic>{
      'headers': instance.headers,
      'rows': instance.rows,
      'normalizedHeaders': instance.normalizedHeaders,
      'validationErrors': instance.validationErrors,
      'headerSuggestions': instance.headerSuggestions,
      'totalRows': instance.totalRows,
    };

_$CsvImportResultImpl _$$CsvImportResultImplFromJson(
        Map<String, dynamic> json) =>
    _$CsvImportResultImpl(
      success: json['success'] as bool,
      rowsProcessed: (json['rowsProcessed'] as num).toInt(),
      rowsImported: (json['rowsImported'] as num).toInt(),
      errors:
          (json['errors'] as List<dynamic>).map((e) => e as String).toList(),
      warnings:
          (json['warnings'] as List<dynamic>).map((e) => e as String).toList(),
      summary: json['summary'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$CsvImportResultImplToJson(
        _$CsvImportResultImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'rowsProcessed': instance.rowsProcessed,
      'rowsImported': instance.rowsImported,
      'errors': instance.errors,
      'warnings': instance.warnings,
      'summary': instance.summary,
    };

_$PushLogEntryImpl _$$PushLogEntryImplFromJson(Map<String, dynamic> json) =>
    _$PushLogEntryImpl(
      id: (json['id'] as num).toInt(),
      timestamp: DateTime.parse(json['timestamp'] as String),
      operation: json['operation'] as String,
      description: json['description'] as String,
      metadata: json['metadata'] as Map<String, dynamic>?,
      user: json['user'] as String?,
      success: json['success'] as bool?,
    );

Map<String, dynamic> _$$PushLogEntryImplToJson(_$PushLogEntryImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'timestamp': instance.timestamp.toIso8601String(),
      'operation': instance.operation,
      'description': instance.description,
      'metadata': instance.metadata,
      'user': instance.user,
      'success': instance.success,
    };

_$PushLogSummaryImpl _$$PushLogSummaryImplFromJson(Map<String, dynamic> json) =>
    _$PushLogSummaryImpl(
      entries: (json['entries'] as List<dynamic>)
          .map((e) => PushLogEntry.fromJson(e as Map<String, dynamic>))
          .toList(),
      totalEntries: (json['totalEntries'] as num).toInt(),
      lastSync: json['lastSync'] == null
          ? null
          : DateTime.parse(json['lastSync'] as String),
      operationsByType:
          (json['operationsByType'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, (e as num).toInt()),
      ),
    );

Map<String, dynamic> _$$PushLogSummaryImplToJson(
        _$PushLogSummaryImpl instance) =>
    <String, dynamic>{
      'entries': instance.entries,
      'totalEntries': instance.totalEntries,
      'lastSync': instance.lastSync?.toIso8601String(),
      'operationsByType': instance.operationsByType,
    };

_$SessionExportImpl _$$SessionExportImplFromJson(Map<String, dynamic> json) =>
    _$SessionExportImpl(
      version: json['version'] as String,
      exportedAt: DateTime.parse(json['exportedAt'] as String),
      context: SessionContext.fromJson(json['context'] as Map<String, dynamic>),
      workbook:
          WorkbookSnapshot.fromJson(json['workbook'] as Map<String, dynamic>),
      settings: json['settings'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$SessionExportImplToJson(_$SessionExportImpl instance) =>
    <String, dynamic>{
      'version': instance.version,
      'exportedAt': instance.exportedAt.toIso8601String(),
      'context': instance.context,
      'workbook': instance.workbook,
      'settings': instance.settings,
    };

_$SessionImportResultImpl _$$SessionImportResultImplFromJson(
        Map<String, dynamic> json) =>
    _$SessionImportResultImpl(
      success: json['success'] as bool,
      importedSheets: (json['importedSheets'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      errors:
          (json['errors'] as List<dynamic>).map((e) => e as String).toList(),
      warnings:
          (json['warnings'] as List<dynamic>).map((e) => e as String).toList(),
      conflicts: json['conflicts'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$SessionImportResultImplToJson(
        _$SessionImportResultImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'importedSheets': instance.importedSheets,
      'errors': instance.errors,
      'warnings': instance.warnings,
      'conflicts': instance.conflicts,
    };
