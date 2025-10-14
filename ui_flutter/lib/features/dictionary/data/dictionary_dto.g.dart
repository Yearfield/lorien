// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dictionary_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$DictionaryTermImpl _$$DictionaryTermImplFromJson(Map<String, dynamic> json) =>
    _$DictionaryTermImpl(
      id: (json['id'] as num).toInt(),
      term: json['term'] as String,
      definition: json['definition'] as String?,
      synonyms: (json['synonyms'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      isRedFlag: json['is_red_flag'] as bool? ?? false,
      avgChildrenCount: (json['avg_children_count'] as num?)?.toInt() ?? 0,
      conflictsCount: (json['conflicts_count'] as num?)?.toInt() ?? 0,
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
    );

Map<String, dynamic> _$$DictionaryTermImplToJson(
        _$DictionaryTermImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'term': instance.term,
      'definition': instance.definition,
      'synonyms': instance.synonyms,
      'is_red_flag': instance.isRedFlag,
      'avg_children_count': instance.avgChildrenCount,
      'conflicts_count': instance.conflictsCount,
      'created_at': instance.createdAt,
      'updated_at': instance.updatedAt,
    };

_$DictionarySearchResultImpl _$$DictionarySearchResultImplFromJson(
        Map<String, dynamic> json) =>
    _$DictionarySearchResultImpl(
      items: (json['items'] as List<dynamic>)
          .map((e) => DictionaryTerm.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: (json['total'] as num).toInt(),
      query: json['query'] as String,
    );

Map<String, dynamic> _$$DictionarySearchResultImplToJson(
        _$DictionarySearchResultImpl instance) =>
    <String, dynamic>{
      'items': instance.items,
      'total': instance.total,
      'query': instance.query,
    };

_$DictionaryUpdateRequestImpl _$$DictionaryUpdateRequestImplFromJson(
        Map<String, dynamic> json) =>
    _$DictionaryUpdateRequestImpl(
      definition: json['definition'] as String?,
      synonyms: (json['synonyms'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      isRedFlag: json['isRedFlag'] as bool?,
    );

Map<String, dynamic> _$$DictionaryUpdateRequestImplToJson(
        _$DictionaryUpdateRequestImpl instance) =>
    <String, dynamic>{
      'definition': instance.definition,
      'synonyms': instance.synonyms,
      'isRedFlag': instance.isRedFlag,
    };

_$DictionaryStatsImpl _$$DictionaryStatsImplFromJson(
        Map<String, dynamic> json) =>
    _$DictionaryStatsImpl(
      totalTerms: (json['totalTerms'] as num).toInt(),
      redFlagTerms: (json['redFlagTerms'] as num).toInt(),
      termsWithDefinitions: (json['termsWithDefinitions'] as num).toInt(),
      termsWithSynonyms: (json['termsWithSynonyms'] as num).toInt(),
      avgChildrenPerTerm: (json['avgChildrenPerTerm'] as num).toDouble(),
      totalConflicts: (json['totalConflicts'] as num).toInt(),
      completionRate: DictionaryCompletionRate.fromJson(
          json['completionRate'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$$DictionaryStatsImplToJson(
        _$DictionaryStatsImpl instance) =>
    <String, dynamic>{
      'totalTerms': instance.totalTerms,
      'redFlagTerms': instance.redFlagTerms,
      'termsWithDefinitions': instance.termsWithDefinitions,
      'termsWithSynonyms': instance.termsWithSynonyms,
      'avgChildrenPerTerm': instance.avgChildrenPerTerm,
      'totalConflicts': instance.totalConflicts,
      'completionRate': instance.completionRate,
    };

_$DictionaryCompletionRateImpl _$$DictionaryCompletionRateImplFromJson(
        Map<String, dynamic> json) =>
    _$DictionaryCompletionRateImpl(
      definitions: (json['definitions'] as num).toDouble(),
      synonyms: (json['synonyms'] as num).toDouble(),
    );

Map<String, dynamic> _$$DictionaryCompletionRateImplToJson(
        _$DictionaryCompletionRateImpl instance) =>
    <String, dynamic>{
      'definitions': instance.definitions,
      'synonyms': instance.synonyms,
    };

_$TreeRelationshipImpl _$$TreeRelationshipImplFromJson(
        Map<String, dynamic> json) =>
    _$TreeRelationshipImpl(
      id: (json['id'] as num).toInt(),
      label: json['label'] as String?,
      depth: (json['depth'] as num).toInt(),
      slot: (json['slot'] as num?)?.toInt(),
      parentId: (json['parent_id'] as num?)?.toInt(),
    );

Map<String, dynamic> _$$TreeRelationshipImplToJson(
        _$TreeRelationshipImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'label': instance.label,
      'depth': instance.depth,
      'slot': instance.slot,
      'parent_id': instance.parentId,
    };

_$DictionaryTreeRelationshipsImpl _$$DictionaryTreeRelationshipsImplFromJson(
        Map<String, dynamic> json) =>
    _$DictionaryTreeRelationshipsImpl(
      term: json['term'] as String,
      nodes: (json['nodes'] as List<dynamic>)
          .map((e) => TreeRelationship.fromJson(e as Map<String, dynamic>))
          .toList(),
      parents: (json['parents'] as List<dynamic>)
          .map((e) => TreeRelationship.fromJson(e as Map<String, dynamic>))
          .toList(),
      children: (json['children'] as List<dynamic>)
          .map((e) => TreeRelationship.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$$DictionaryTreeRelationshipsImplToJson(
        _$DictionaryTreeRelationshipsImpl instance) =>
    <String, dynamic>{
      'term': instance.term,
      'nodes': instance.nodes,
      'parents': instance.parents,
      'children': instance.children,
    };
