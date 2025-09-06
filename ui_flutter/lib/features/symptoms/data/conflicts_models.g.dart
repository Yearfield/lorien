// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'conflicts_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ConflictItemImpl _$$ConflictItemImplFromJson(Map<String, dynamic> json) =>
    _$ConflictItemImpl(
      id: (json['id'] as num).toInt(),
      type: $enumDecode(_$ConflictTypeEnumMap, json['type']),
      description: json['description'] as String,
      affectedNodes: (json['affectedNodes'] as List<dynamic>)
          .map((e) => (e as num).toInt())
          .toList(),
      affectedLabels: (json['affectedLabels'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      parentId: (json['parentId'] as num?)?.toInt(),
      depth: (json['depth'] as num?)?.toInt(),
      resolution: json['resolution'] as String?,
      detectedAt: json['detectedAt'] == null
          ? null
          : DateTime.parse(json['detectedAt'] as String),
    );

Map<String, dynamic> _$$ConflictItemImplToJson(_$ConflictItemImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'type': _$ConflictTypeEnumMap[instance.type]!,
      'description': instance.description,
      'affectedNodes': instance.affectedNodes,
      'affectedLabels': instance.affectedLabels,
      'parentId': instance.parentId,
      'depth': instance.depth,
      'resolution': instance.resolution,
      'detectedAt': instance.detectedAt?.toIso8601String(),
    };

const _$ConflictTypeEnumMap = {
  ConflictType.duplicateLabels: 'duplicate_labels',
  ConflictType.orphans: 'orphans',
  ConflictType.depthAnomalies: 'depth_anomalies',
  ConflictType.missingSlots: 'missing_slots',
  ConflictType.invalidReferences: 'invalid_references',
};

_$ConflictGroupImpl _$$ConflictGroupImplFromJson(Map<String, dynamic> json) =>
    _$ConflictGroupImpl(
      type: $enumDecode(_$ConflictTypeEnumMap, json['type']),
      items: (json['items'] as List<dynamic>)
          .map((e) => ConflictItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      totalCount: (json['totalCount'] as num).toInt(),
      summary: json['summary'] as String?,
    );

Map<String, dynamic> _$$ConflictGroupImplToJson(_$ConflictGroupImpl instance) =>
    <String, dynamic>{
      'type': _$ConflictTypeEnumMap[instance.type]!,
      'items': instance.items,
      'totalCount': instance.totalCount,
      'summary': instance.summary,
    };

_$ConflictsReportImpl _$$ConflictsReportImplFromJson(
        Map<String, dynamic> json) =>
    _$ConflictsReportImpl(
      groups: (json['groups'] as List<dynamic>)
          .map((e) => ConflictGroup.fromJson(e as Map<String, dynamic>))
          .toList(),
      totalConflicts: (json['totalConflicts'] as num).toInt(),
      generatedAt: json['generatedAt'] == null
          ? null
          : DateTime.parse(json['generatedAt'] as String),
      byType: (json['byType'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, (e as num).toInt()),
      ),
    );

Map<String, dynamic> _$$ConflictsReportImplToJson(
        _$ConflictsReportImpl instance) =>
    <String, dynamic>{
      'groups': instance.groups,
      'totalConflicts': instance.totalConflicts,
      'generatedAt': instance.generatedAt?.toIso8601String(),
      'byType': instance.byType,
    };

_$ConflictResolutionImpl _$$ConflictResolutionImplFromJson(
        Map<String, dynamic> json) =>
    _$ConflictResolutionImpl(
      conflictId: (json['conflictId'] as num).toInt(),
      action: json['action'] as String,
      newValue: json['newValue'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$ConflictResolutionImplToJson(
        _$ConflictResolutionImpl instance) =>
    <String, dynamic>{
      'conflictId': instance.conflictId,
      'action': instance.action,
      'newValue': instance.newValue,
      'metadata': instance.metadata,
    };
