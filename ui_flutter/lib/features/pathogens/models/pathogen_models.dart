import 'package:freezed_annotation/freezed_annotation.dart';

part 'pathogen_models.freezed.dart';
part 'pathogen_models.g.dart';

@freezed
class Pathogen with _$Pathogen {
  const factory Pathogen({
    required int id,
    String? classification,
    String? nt,
    @JsonKey(name: 'pathogen_id') String? pathogenId,
    @JsonKey(name: 'pathogen_name') required String pathogenName,
    String? vaccine,
    String? toxin,
    String? transmission,
    @JsonKey(name: 'ab_resistance') String? abResistance,
    String? host,
    String? commensal,
    String? disease,
    String? incubation,
    String? diagnosis,
    String? treatment,
    String? prevention,
    String? notes,
    @JsonKey(name: 'created_at') required String createdAt,
    @JsonKey(name: 'updated_at') required String updatedAt,
  }) = _Pathogen;

  factory Pathogen.fromJson(Map<String, dynamic> json) => _$PathogenFromJson(json);
}

@freezed
class AssociationType with _$AssociationType {
  const factory AssociationType({
    required int id,
    required String name,
    String? description,
    @JsonKey(name: 'created_at') required String createdAt,
  }) = _AssociationType;

  factory AssociationType.fromJson(Map<String, dynamic> json) => _$AssociationTypeFromJson(json);

  // Helper method to create from string (for the simple API response)
  factory AssociationType.fromString(String name) => AssociationType(
    id: 0, // Will be set by the server
    name: name,
    description: null,
    createdAt: DateTime.now().toIso8601String(),
  );
}

@freezed
class PathogenAssociation with _$PathogenAssociation {
  const factory PathogenAssociation({
    @JsonKey(name: 'pathogen_id') required int pathogenId,
    @JsonKey(name: 'association_type_id') required int associationTypeId,
    required int value,
    @JsonKey(name: 'association_type_name') String? associationTypeName,
  }) = _PathogenAssociation;

  factory PathogenAssociation.fromJson(Map<String, dynamic> json) => _$PathogenAssociationFromJson(json);
}

@freezed
class PathogenWithAssociations with _$PathogenWithAssociations {
  const factory PathogenWithAssociations({
    required int id,
    String? classification,
    String? nt,
    @JsonKey(name: 'pathogen_id') String? pathogenId,
    @JsonKey(name: 'pathogen_name') required String pathogenName,
    String? vaccine,
    String? toxin,
    String? transmission,
    @JsonKey(name: 'ab_resistance') String? abResistance,
    String? host,
    String? commensal,
    String? disease,
    String? incubation,
    String? diagnosis,
    String? treatment,
    String? prevention,
    String? notes,
    @JsonKey(name: 'created_at') required String createdAt,
    @JsonKey(name: 'updated_at') required String updatedAt,
    required List<PathogenAssociation> associations,
  }) = _PathogenWithAssociations;

  factory PathogenWithAssociations.fromJson(Map<String, dynamic> json) => _$PathogenWithAssociationsFromJson(json);
}

@freezed
class PathogenStats with _$PathogenStats {
  const factory PathogenStats({
    @JsonKey(name: 'total_pathogens') required int totalPathogens,
    @JsonKey(name: 'total_associations') required int totalAssociations,
    @JsonKey(name: 'pathogens_with_associations') required int pathogensWithAssociations,
    @JsonKey(name: 'average_associations_per_pathogen') required double averageAssociationsPerPathogen,
  }) = _PathogenStats;

  factory PathogenStats.fromJson(Map<String, dynamic> json) => _$PathogenStatsFromJson(json);
}

@freezed
class PathogenImportResult with _$PathogenImportResult {
  const factory PathogenImportResult({
    required bool success,
    @JsonKey(name: 'pathogens_processed') required int pathogensProcessed,
    @JsonKey(name: 'pathogens_created') required int pathogensCreated,
    @JsonKey(name: 'pathogens_updated') required int pathogensUpdated,
    @JsonKey(name: 'associations_processed') required int associationsProcessed,
    @JsonKey(name: 'associations_created') required int associationsCreated,
    required List<String> errors,
    required List<String> warnings,
  }) = _PathogenImportResult;

  factory PathogenImportResult.fromJson(Map<String, dynamic> json) => _$PathogenImportResultFromJson(json);
}

@freezed
class PathogenProperties with _$PathogenProperties {
  const factory PathogenProperties({
    String? classification,
    String? nt,
    @JsonKey(name: 'pathogen_id') String? pathogenId,
    @JsonKey(name: 'pathogen_name') required String pathogenName,
    String? vaccine,
    String? toxin,
    String? transmission,
    @JsonKey(name: 'ab_resistance') String? abResistance,
    String? host,
    String? commensal,
    String? disease,
    String? incubation,
    String? diagnosis,
    String? treatment,
    String? prevention,
    String? notes,
  }) = _PathogenProperties;

  factory PathogenProperties.fromJson(Map<String, dynamic> json) => _$PathogenPropertiesFromJson(json);
}
