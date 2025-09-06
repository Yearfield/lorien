// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workspace_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ImportJobImpl _$$ImportJobImplFromJson(Map<String, dynamic> json) =>
    _$ImportJobImpl(
      id: json['id'] as String,
      fileName: json['fileName'] as String,
      status: json['status'] as String,
      startedAt: DateTime.parse(json['startedAt'] as String),
      completedAt: json['completedAt'] == null
          ? null
          : DateTime.parse(json['completedAt'] as String),
      totalRows: (json['totalRows'] as num).toInt(),
      processedRows: (json['processedRows'] as num).toInt(),
      importedRows: (json['importedRows'] as num).toInt(),
      errors:
          (json['errors'] as List<dynamic>?)?.map((e) => e as String).toList(),
      warnings: (json['warnings'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      headerMapping: json['headerMapping'] as Map<String, dynamic>?,
      validationResults: json['validationResults'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$ImportJobImplToJson(_$ImportJobImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'fileName': instance.fileName,
      'status': instance.status,
      'startedAt': instance.startedAt.toIso8601String(),
      'completedAt': instance.completedAt?.toIso8601String(),
      'totalRows': instance.totalRows,
      'processedRows': instance.processedRows,
      'importedRows': instance.importedRows,
      'errors': instance.errors,
      'warnings': instance.warnings,
      'headerMapping': instance.headerMapping,
      'validationResults': instance.validationResults,
    };

_$BackupRestoreStatusImpl _$$BackupRestoreStatusImplFromJson(
        Map<String, dynamic> json) =>
    _$BackupRestoreStatusImpl(
      operation: json['operation'] as String,
      status: json['status'] as String,
      startedAt: DateTime.parse(json['startedAt'] as String),
      completedAt: json['completedAt'] == null
          ? null
          : DateTime.parse(json['completedAt'] as String),
      totalItems: (json['totalItems'] as num).toInt(),
      processedItems: (json['processedItems'] as num).toInt(),
      errorMessage: json['errorMessage'] as String?,
      details: json['details'] as Map<String, dynamic>?,
      integrityCheckPassed: json['integrityCheckPassed'] as bool?,
    );

Map<String, dynamic> _$$BackupRestoreStatusImplToJson(
        _$BackupRestoreStatusImpl instance) =>
    <String, dynamic>{
      'operation': instance.operation,
      'status': instance.status,
      'startedAt': instance.startedAt.toIso8601String(),
      'completedAt': instance.completedAt?.toIso8601String(),
      'totalItems': instance.totalItems,
      'processedItems': instance.processedItems,
      'errorMessage': instance.errorMessage,
      'details': instance.details,
      'integrityCheckPassed': instance.integrityCheckPassed,
    };

_$HeaderValidationErrorImpl _$$HeaderValidationErrorImplFromJson(
        Map<String, dynamic> json) =>
    _$HeaderValidationErrorImpl(
      row: (json['row'] as num).toInt(),
      colIndex: (json['colIndex'] as num).toInt(),
      expected: json['expected'] as String,
      received: json['received'] as String,
      suggestion: json['suggestion'] as String?,
    );

Map<String, dynamic> _$$HeaderValidationErrorImplToJson(
        _$HeaderValidationErrorImpl instance) =>
    <String, dynamic>{
      'row': instance.row,
      'colIndex': instance.colIndex,
      'expected': instance.expected,
      'received': instance.received,
      'suggestion': instance.suggestion,
    };

_$ImportValidationResultImpl _$$ImportValidationResultImplFromJson(
        Map<String, dynamic> json) =>
    _$ImportValidationResultImpl(
      isValid: json['isValid'] as bool,
      headerErrors: (json['headerErrors'] as List<dynamic>?)
          ?.map(
              (e) => HeaderValidationError.fromJson(e as Map<String, dynamic>))
          .toList(),
      typeCounts: (json['typeCounts'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, (e as num).toInt()),
      ),
      generalErrors: (json['generalErrors'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      preview: json['preview'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$ImportValidationResultImplToJson(
        _$ImportValidationResultImpl instance) =>
    <String, dynamic>{
      'isValid': instance.isValid,
      'headerErrors': instance.headerErrors,
      'typeCounts': instance.typeCounts,
      'generalErrors': instance.generalErrors,
      'preview': instance.preview,
    };

_$BackupMetadataImpl _$$BackupMetadataImplFromJson(Map<String, dynamic> json) =>
    _$BackupMetadataImpl(
      version: json['version'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      checksum: json['checksum'] as String,
      recordCounts: Map<String, int>.from(json['recordCounts'] as Map),
      settings: json['settings'] as Map<String, dynamic>?,
      description: json['description'] as String?,
    );

Map<String, dynamic> _$$BackupMetadataImplToJson(
        _$BackupMetadataImpl instance) =>
    <String, dynamic>{
      'version': instance.version,
      'createdAt': instance.createdAt.toIso8601String(),
      'checksum': instance.checksum,
      'recordCounts': instance.recordCounts,
      'settings': instance.settings,
      'description': instance.description,
    };
