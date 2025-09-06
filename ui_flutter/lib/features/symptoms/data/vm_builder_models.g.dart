// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'vm_builder_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$VitalMeasurementDraftImpl _$$VitalMeasurementDraftImplFromJson(
        Map<String, dynamic> json) =>
    _$VitalMeasurementDraftImpl(
      label: json['label'] as String,
      nodes: (json['nodes'] as List<dynamic>?)
          ?.map((e) => NodeDraft.fromJson(e as Map<String, dynamic>))
          .toList(),
      isTemplate: json['isTemplate'] as bool?,
    );

Map<String, dynamic> _$$VitalMeasurementDraftImplToJson(
        _$VitalMeasurementDraftImpl instance) =>
    <String, dynamic>{
      'label': instance.label,
      'nodes': instance.nodes,
      'isTemplate': instance.isTemplate,
    };

_$NodeDraftImpl _$$NodeDraftImplFromJson(Map<String, dynamic> json) =>
    _$NodeDraftImpl(
      depth: (json['depth'] as num).toInt(),
      slot: (json['slot'] as num).toInt(),
      label: json['label'] as String,
      children: (json['children'] as List<dynamic>?)
          ?.map((e) => NodeDraft.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$$NodeDraftImplToJson(_$NodeDraftImpl instance) =>
    <String, dynamic>{
      'depth': instance.depth,
      'slot': instance.slot,
      'label': instance.label,
      'children': instance.children,
    };

_$SheetDraftImpl _$$SheetDraftImplFromJson(Map<String, dynamic> json) =>
    _$SheetDraftImpl(
      name: json['name'] as String,
      vitalMeasurements: (json['vitalMeasurements'] as List<dynamic>)
          .map((e) => VitalMeasurementDraft.fromJson(e as Map<String, dynamic>))
          .toList(),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$SheetDraftImplToJson(_$SheetDraftImpl instance) =>
    <String, dynamic>{
      'name': instance.name,
      'vitalMeasurements': instance.vitalMeasurements,
      'metadata': instance.metadata,
    };

_$ValidationResultImpl _$$ValidationResultImplFromJson(
        Map<String, dynamic> json) =>
    _$ValidationResultImpl(
      isValid: json['isValid'] as bool,
      errors:
          (json['errors'] as List<dynamic>?)?.map((e) => e as String).toList(),
      warnings: (json['warnings'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      suggestions: json['suggestions'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$ValidationResultImplToJson(
        _$ValidationResultImpl instance) =>
    <String, dynamic>{
      'isValid': instance.isValid,
      'errors': instance.errors,
      'warnings': instance.warnings,
      'suggestions': instance.suggestions,
    };

_$CreationResultImpl _$$CreationResultImplFromJson(Map<String, dynamic> json) =>
    _$CreationResultImpl(
      success: json['success'] as bool,
      createdVmIds: (json['createdVmIds'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList(),
      createdNodeIds: (json['createdNodeIds'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList(),
      materializationResult: json['materializationResult'] == null
          ? null
          : MaterializationResult.fromJson(
              json['materializationResult'] as Map<String, dynamic>),
      errors:
          (json['errors'] as List<dynamic>?)?.map((e) => e as String).toList(),
    );

Map<String, dynamic> _$$CreationResultImplToJson(
        _$CreationResultImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'createdVmIds': instance.createdVmIds,
      'createdNodeIds': instance.createdNodeIds,
      'materializationResult': instance.materializationResult,
      'errors': instance.errors,
    };

_$DuplicateCheckResultImpl _$$DuplicateCheckResultImplFromJson(
        Map<String, dynamic> json) =>
    _$DuplicateCheckResultImpl(
      hasDuplicates: json['hasDuplicates'] as bool,
      duplicateLabels: (json['duplicateLabels'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      conflicts: (json['conflicts'] as Map<String, dynamic>?)?.map(
        (k, e) =>
            MapEntry(k, (e as List<dynamic>).map((e) => e as String).toList()),
      ),
    );

Map<String, dynamic> _$$DuplicateCheckResultImplToJson(
        _$DuplicateCheckResultImpl instance) =>
    <String, dynamic>{
      'hasDuplicates': instance.hasDuplicates,
      'duplicateLabels': instance.duplicateLabels,
      'conflicts': instance.conflicts,
    };
