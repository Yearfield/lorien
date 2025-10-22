import 'package:freezed_annotation/freezed_annotation.dart';

part 'warhammer_models.freezed.dart';
part 'warhammer_models.g.dart';

@freezed
class Symptom with _$Symptom {
  const factory Symptom({
    required int id,
    @JsonKey(name: 'symptom_name') required String symptomName,
    required double probability,
    @JsonKey(name: 'created_at') required String createdAt,
    @JsonKey(name: 'updated_at') required String updatedAt,
  }) = _Symptom;

  factory Symptom.fromJson(Map<String, dynamic> json) => _$SymptomFromJson(json);
}

@freezed
class Disease with _$Disease {
  const factory Disease({
    required int id,
    @JsonKey(name: 'disease_name') required String diseaseName,
    @JsonKey(name: 'estimated_lifetime_risk') required double estimatedLifetimeRisk,
    @JsonKey(name: 'created_at') required String createdAt,
    @JsonKey(name: 'updated_at') required String updatedAt,
  }) = _Disease;

  factory Disease.fromJson(Map<String, dynamic> json) => _$DiseaseFromJson(json);
}

@freezed
class DiseaseResult with _$DiseaseResult {
  const factory DiseaseResult({
    required String disease,
    required double probability,
  }) = _DiseaseResult;

  factory DiseaseResult.fromJson(Map<String, dynamic> json) => _$DiseaseResultFromJson(json);
}

@freezed
class CalculationRequest with _$CalculationRequest {
  const factory CalculationRequest({
    required List<String> symptoms,
  }) = _CalculationRequest;

  factory CalculationRequest.fromJson(Map<String, dynamic> json) => _$CalculationRequestFromJson(json);
}

@freezed
class CalculationResponse with _$CalculationResponse {
  const factory CalculationResponse({
    int? calculationId,
    required List<String> inputSymptoms,
    required List<DiseaseResult> results,
    required String timestamp,
    @Default([]) List<String> errors,
  }) = _CalculationResponse;

  factory CalculationResponse.fromJson(Map<String, dynamic> json) => _$CalculationResponseFromJson(json);
}

@freezed
class ImportResultResponse with _$ImportResultResponse {
  const factory ImportResultResponse({
    required bool success,
    @Default(0) int diseasesProcessed,
    @Default(0) int diseasesCreated,
    @Default(0) int diseasesUpdated,
    @Default(0) int symptomsProcessed,
    @Default(0) int symptomsCreated,
    @Default(0) int symptomsUpdated,
    @Default(0) int conditionalsProcessed,
    @Default(0) int conditionalsCreated,
    @Default(0) int conditionalsUpdated,
    @Default([]) List<String> errors,
    @Default([]) List<String> warnings,
  }) = _ImportResultResponse;

  factory ImportResultResponse.fromJson(Map<String, dynamic> json) => _$ImportResultResponseFromJson(json);
}

@freezed
class WarhammerStats with _$WarhammerStats {
  const factory WarhammerStats({
    @JsonKey(name: 'total_diseases') required int totalDiseases,
    @JsonKey(name: 'total_symptoms') required int totalSymptoms,
    @JsonKey(name: 'total_conditionals') required int totalConditionals,
    @JsonKey(name: 'total_calculations') required int totalCalculations,
    @JsonKey(name: 'saved_calculations') required int savedCalculations,
  }) = _WarhammerStats;

  factory WarhammerStats.fromJson(Map<String, dynamic> json) => _$WarhammerStatsFromJson(json);
}

@freezed
class SavedCalculation with _$SavedCalculation {
  const factory SavedCalculation({
    required int id,
    required String calculationDate,
    required List<String> inputSymptoms,
    required List<DiseaseResult> results,
    required bool saved,
  }) = _SavedCalculation;

  factory SavedCalculation.fromJson(Map<String, dynamic> json) => _$SavedCalculationFromJson(json);
}

@freezed
class NormalizedMatch with _$NormalizedMatch {
  const factory NormalizedMatch({
    @JsonKey(name: 'decision_tree') required String decisionTree,
    @JsonKey(name: 'warhammer') required String warhammer,
    @JsonKey(name: 'normalized') required String normalized,
  }) = _NormalizedMatch;

  factory NormalizedMatch.fromJson(Map<String, dynamic> json) =>
      _$NormalizedMatchFromJson(json);
}

@freezed
class SymptomSynonym with _$SymptomSynonym {
  const factory SymptomSynonym({
    required int id,
    @JsonKey(name: 'warhammer_symptom') required String warhammerSymptom,
    @JsonKey(name: 'decision_tree_symptom') required String decisionTreeSymptom,
    @JsonKey(name: 'created_at') required String createdAt,
    @JsonKey(name: 'updated_at') required String updatedAt,
  }) = _SymptomSynonym;

  factory SymptomSynonym.fromJson(Map<String, dynamic> json) =>
      _$SymptomSynonymFromJson(json);
}

@freezed
class CreateSynonymRequest with _$CreateSynonymRequest {
  const factory CreateSynonymRequest({
    @JsonKey(name: 'warhammer_symptom') required String warhammerSymptom,
    @JsonKey(name: 'decision_tree_symptom') required String decisionTreeSymptom,
  }) = _CreateSynonymRequest;

  factory CreateSynonymRequest.fromJson(Map<String, dynamic> json) =>
      _$CreateSynonymRequestFromJson(json);
}

@freezed
class SymptomComparison with _$SymptomComparison {
  const factory SymptomComparison({
    @JsonKey(name: 'decision_tree_symptoms') @Default([]) List<String> decisionTreeSymptoms,
    @JsonKey(name: 'warhammer_symptoms') @Default([]) List<String> warhammerSymptoms,
    @JsonKey(name: 'matching_symptoms') @Default([]) List<String> matchingSymptoms,
    @JsonKey(name: 'missing_from_warhammer') @Default([]) List<String> missingFromWarhammer,
    @JsonKey(name: 'extra_in_warhammer') @Default([]) List<String> extraInWarhammer,
    @JsonKey(name: 'total_decision_tree') @Default(0) int totalDecisionTree,
    @JsonKey(name: 'total_warhammer') @Default(0) int totalWarhammer,
    @JsonKey(name: 'match_count') @Default(0) int matchCount,
    @JsonKey(name: 'normalized_matches') @Default([]) List<NormalizedMatch> normalizedMatches,
  }) = _SymptomComparison;

  factory SymptomComparison.fromJson(Map<String, dynamic> json) => _$SymptomComparisonFromJson(json);
}
