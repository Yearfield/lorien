import 'package:freezed_annotation/freezed_annotation.dart';

part 'dictionary_dto.freezed.dart';
part 'dictionary_dto.g.dart';

@freezed
class DictionaryTerm with _$DictionaryTerm {
  const factory DictionaryTerm({
    required int id,
    required String term,
    String? definition,
    @Default([]) List<String> synonyms,
    @Default(false) bool isRedFlag,
    @Default(0) int avgChildrenCount,
    @Default(0) int conflictsCount,
    required String createdAt,
    required String updatedAt,
  }) = _DictionaryTerm;

  factory DictionaryTerm.fromJson(Map<String, dynamic> json) =>
      _$DictionaryTermFromJson(json);
}

@freezed
class DictionarySearchResult with _$DictionarySearchResult {
  const factory DictionarySearchResult({
    required List<DictionaryTerm> items,
    required int total,
    required String query,
  }) = _DictionarySearchResult;

  factory DictionarySearchResult.fromJson(Map<String, dynamic> json) =>
      _$DictionarySearchResultFromJson(json);
}

@freezed
class DictionaryUpdateRequest with _$DictionaryUpdateRequest {
  const factory DictionaryUpdateRequest({
    String? definition,
    List<String>? synonyms,
    bool? isRedFlag,
  }) = _DictionaryUpdateRequest;

  factory DictionaryUpdateRequest.fromJson(Map<String, dynamic> json) =>
      _$DictionaryUpdateRequestFromJson(json);
}

@freezed
class DictionaryStats with _$DictionaryStats {
  const factory DictionaryStats({
    required int totalTerms,
    required int redFlagTerms,
    required int termsWithDefinitions,
    required int termsWithSynonyms,
    required double avgChildrenPerTerm,
    required int totalConflicts,
    required DictionaryCompletionRate completionRate,
  }) = _DictionaryStats;

  factory DictionaryStats.fromJson(Map<String, dynamic> json) {
    // Handle potential null values from API
    return DictionaryStats(
      totalTerms: (json['total_terms'] as num?)?.toInt() ?? 0,
      redFlagTerms: (json['red_flag_terms'] as num?)?.toInt() ?? 0,
      termsWithDefinitions: (json['terms_with_definitions'] as num?)?.toInt() ?? 0,
      termsWithSynonyms: (json['terms_with_synonyms'] as num?)?.toInt() ?? 0,
      avgChildrenPerTerm: (json['avg_children_per_term'] as num?)?.toDouble() ?? 0.0,
      totalConflicts: (json['total_conflicts'] as num?)?.toInt() ?? 0,
      completionRate: DictionaryCompletionRate.fromJson(
        json['completion_rate'] as Map<String, dynamic>? ?? {
          'definitions': 0.0,
          'synonyms': 0.0,
        },
      ),
    );
  }
}

@freezed
class DictionaryCompletionRate with _$DictionaryCompletionRate {
  const factory DictionaryCompletionRate({
    required double definitions,
    required double synonyms,
  }) = _DictionaryCompletionRate;

  factory DictionaryCompletionRate.fromJson(Map<String, dynamic> json) {
    return DictionaryCompletionRate(
      definitions: (json['definitions'] as num?)?.toDouble() ?? 0.0,
      synonyms: (json['synonyms'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

@freezed
class TreeRelationship with _$TreeRelationship {
  const factory TreeRelationship({
    required int id,
    String? label,
    required int depth,
    int? slot,
    @JsonKey(name: 'parent_id') int? parentId,
  }) = _TreeRelationship;

  factory TreeRelationship.fromJson(Map<String, dynamic> json) =>
      _$TreeRelationshipFromJson(json);
}

@freezed
class DictionaryTreeRelationships with _$DictionaryTreeRelationships {
  const factory DictionaryTreeRelationships({
    required String term,
    required List<TreeRelationship> nodes,
    required List<TreeRelationship> parents,
    required List<TreeRelationship> children,
  }) = _DictionaryTreeRelationships;

  factory DictionaryTreeRelationships.fromJson(Map<String, dynamic> json) =>
      _$DictionaryTreeRelationshipsFromJson(json);
}
