// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'symptoms_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$IncompleteParentImpl _$$IncompleteParentImplFromJson(
        Map<String, dynamic> json) =>
    _$IncompleteParentImpl(
      parentId: (json['parentId'] as num).toInt(),
      label: json['label'] as String,
      depth: (json['depth'] as num).toInt(),
      missingSlots: (json['missingSlots'] as List<dynamic>)
          .map((e) => (e as num).toInt())
          .toList(),
      path: json['path'] as String,
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$$IncompleteParentImplToJson(
        _$IncompleteParentImpl instance) =>
    <String, dynamic>{
      'parentId': instance.parentId,
      'label': instance.label,
      'depth': instance.depth,
      'missingSlots': instance.missingSlots,
      'path': instance.path,
      'updatedAt': instance.updatedAt.toIso8601String(),
    };

_$ChildSlotImpl _$$ChildSlotImplFromJson(Map<String, dynamic> json) =>
    _$ChildSlotImpl(
      slot: (json['slot'] as num).toInt(),
      label: json['label'] as String?,
      nodeId: (json['nodeId'] as num?)?.toInt(),
      existing: json['existing'] as bool?,
      error: json['error'] as String?,
      warning: json['warning'] as String?,
    );

Map<String, dynamic> _$$ChildSlotImplToJson(_$ChildSlotImpl instance) =>
    <String, dynamic>{
      'slot': instance.slot,
      'label': instance.label,
      'nodeId': instance.nodeId,
      'existing': instance.existing,
      'error': instance.error,
      'warning': instance.warning,
    };

_$ParentChildrenImpl _$$ParentChildrenImplFromJson(Map<String, dynamic> json) =>
    _$ParentChildrenImpl(
      parentId: (json['parentId'] as num).toInt(),
      parentLabel: json['parentLabel'] as String,
      depth: (json['depth'] as num).toInt(),
      path: json['path'] as String,
      children: (json['children'] as List<dynamic>)
          .map((e) => ChildSlot.fromJson(e as Map<String, dynamic>))
          .toList(),
      missingSlots: (json['missingSlots'] as List<dynamic>)
          .map((e) => (e as num).toInt())
          .toList(),
      version: json['version'] as String?,
      etag: json['etag'] as String?,
    );

Map<String, dynamic> _$$ParentChildrenImplToJson(
        _$ParentChildrenImpl instance) =>
    <String, dynamic>{
      'parentId': instance.parentId,
      'parentLabel': instance.parentLabel,
      'depth': instance.depth,
      'path': instance.path,
      'children': instance.children,
      'missingSlots': instance.missingSlots,
      'version': instance.version,
      'etag': instance.etag,
    };

_$BatchAddRequestImpl _$$BatchAddRequestImplFromJson(
        Map<String, dynamic> json) =>
    _$BatchAddRequestImpl(
      labels:
          (json['labels'] as List<dynamic>).map((e) => e as String).toList(),
      replaceExisting: json['replaceExisting'] as bool?,
    );

Map<String, dynamic> _$$BatchAddRequestImplToJson(
        _$BatchAddRequestImpl instance) =>
    <String, dynamic>{
      'labels': instance.labels,
      'replaceExisting': instance.replaceExisting,
    };

_$DictionarySuggestionImpl _$$DictionarySuggestionImplFromJson(
        Map<String, dynamic> json) =>
    _$DictionarySuggestionImpl(
      id: (json['id'] as num).toInt(),
      term: json['term'] as String,
      normalized: json['normalized'] as String,
      hints: json['hints'] as String?,
      isRedFlag: json['isRedFlag'] as bool?,
    );

Map<String, dynamic> _$$DictionarySuggestionImplToJson(
        _$DictionarySuggestionImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'term': instance.term,
      'normalized': instance.normalized,
      'hints': instance.hints,
      'isRedFlag': instance.isRedFlag,
    };

_$ParentStatusImpl _$$ParentStatusImplFromJson(Map<String, dynamic> json) =>
    _$ParentStatusImpl(
      status: json['status'] as String,
      message: json['message'] as String?,
      filledCount: (json['filledCount'] as num?)?.toInt(),
      totalCount: (json['totalCount'] as num?)?.toInt(),
    );

Map<String, dynamic> _$$ParentStatusImplToJson(_$ParentStatusImpl instance) =>
    <String, dynamic>{
      'status': instance.status,
      'message': instance.message,
      'filledCount': instance.filledCount,
      'totalCount': instance.totalCount,
    };

_$ChildrenUpdateInImpl _$$ChildrenUpdateInImplFromJson(
        Map<String, dynamic> json) =>
    _$ChildrenUpdateInImpl(
      version: json['version'] as String?,
      children: (json['children'] as List<dynamic>)
          .map((e) => ChildSlot.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$$ChildrenUpdateInImplToJson(
        _$ChildrenUpdateInImpl instance) =>
    <String, dynamic>{
      'version': instance.version,
      'children': instance.children,
    };

_$ChildrenUpdateOutImpl _$$ChildrenUpdateOutImplFromJson(
        Map<String, dynamic> json) =>
    _$ChildrenUpdateOutImpl(
      parentId: (json['parentId'] as num).toInt(),
      version: (json['version'] as num).toInt(),
      missingSlots: (json['missingSlots'] as List<dynamic>)
          .map((e) => (e as num).toInt())
          .toList(),
      updated: (json['updated'] as List<dynamic>)
          .map((e) => (e as num).toInt())
          .toList(),
    );

Map<String, dynamic> _$$ChildrenUpdateOutImplToJson(
        _$ChildrenUpdateOutImpl instance) =>
    <String, dynamic>{
      'parentId': instance.parentId,
      'version': instance.version,
      'missingSlots': instance.missingSlots,
      'updated': instance.updated,
    };

_$MaterializationResultImpl _$$MaterializationResultImplFromJson(
        Map<String, dynamic> json) =>
    _$MaterializationResultImpl(
      added: (json['added'] as num).toInt(),
      filled: (json['filled'] as num).toInt(),
      pruned: (json['pruned'] as num).toInt(),
      kept: (json['kept'] as num).toInt(),
      log: json['log'] as String?,
      timestamp: json['timestamp'] == null
          ? null
          : DateTime.parse(json['timestamp'] as String),
      details:
          (json['details'] as List<dynamic>?)?.map((e) => e as String).toList(),
    );

Map<String, dynamic> _$$MaterializationResultImplToJson(
        _$MaterializationResultImpl instance) =>
    <String, dynamic>{
      'added': instance.added,
      'filled': instance.filled,
      'pruned': instance.pruned,
      'kept': instance.kept,
      'log': instance.log,
      'timestamp': instance.timestamp?.toIso8601String(),
      'details': instance.details,
    };

_$MaterializationHistoryItemImpl _$$MaterializationHistoryItemImplFromJson(
        Map<String, dynamic> json) =>
    _$MaterializationHistoryItemImpl(
      id: (json['id'] as num).toInt(),
      timestamp: DateTime.parse(json['timestamp'] as String),
      operation: json['operation'] as String,
      result: MaterializationResult.fromJson(
          json['result'] as Map<String, dynamic>),
      parentIds: (json['parentIds'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList(),
      description: json['description'] as String?,
    );

Map<String, dynamic> _$$MaterializationHistoryItemImplToJson(
        _$MaterializationHistoryItemImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'timestamp': instance.timestamp.toIso8601String(),
      'operation': instance.operation,
      'result': instance.result,
      'parentIds': instance.parentIds,
      'description': instance.description,
    };

_$MaterializationPreviewImpl _$$MaterializationPreviewImplFromJson(
        Map<String, dynamic> json) =>
    _$MaterializationPreviewImpl(
      parentId: (json['parentId'] as num).toInt(),
      willAdd:
          (json['willAdd'] as List<dynamic>).map((e) => e as String).toList(),
      willFill:
          (json['willFill'] as List<dynamic>).map((e) => e as String).toList(),
      willPrune:
          (json['willPrune'] as List<dynamic>).map((e) => e as String).toList(),
      willKeep:
          (json['willKeep'] as List<dynamic>).map((e) => e as String).toList(),
      warnings: json['warnings'] as String?,
      canUndo: json['canUndo'] as bool?,
    );

Map<String, dynamic> _$$MaterializationPreviewImplToJson(
        _$MaterializationPreviewImpl instance) =>
    <String, dynamic>{
      'parentId': instance.parentId,
      'willAdd': instance.willAdd,
      'willFill': instance.willFill,
      'willPrune': instance.willPrune,
      'willKeep': instance.willKeep,
      'warnings': instance.warnings,
      'canUndo': instance.canUndo,
    };

_$MaterializationStatsImpl _$$MaterializationStatsImplFromJson(
        Map<String, dynamic> json) =>
    _$MaterializationStatsImpl(
      totalMaterializations: (json['totalMaterializations'] as num).toInt(),
      totalAdded: (json['totalAdded'] as num).toInt(),
      totalFilled: (json['totalFilled'] as num).toInt(),
      totalPruned: (json['totalPruned'] as num).toInt(),
      totalKept: (json['totalKept'] as num).toInt(),
      lastMaterialization: json['lastMaterialization'] == null
          ? null
          : DateTime.parse(json['lastMaterialization'] as String),
      byOperationType: (json['byOperationType'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, (e as num).toInt()),
      ),
    );

Map<String, dynamic> _$$MaterializationStatsImplToJson(
        _$MaterializationStatsImpl instance) =>
    <String, dynamic>{
      'totalMaterializations': instance.totalMaterializations,
      'totalAdded': instance.totalAdded,
      'totalFilled': instance.totalFilled,
      'totalPruned': instance.totalPruned,
      'totalKept': instance.totalKept,
      'lastMaterialization': instance.lastMaterialization?.toIso8601String(),
      'byOperationType': instance.byOperationType,
    };
