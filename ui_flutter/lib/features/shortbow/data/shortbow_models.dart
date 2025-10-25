import 'package:freezed_annotation/freezed_annotation.dart';

part 'shortbow_models.freezed.dart';
part 'shortbow_models.g.dart';

@freezed
class ShortBowSymptom with _$ShortBowSymptom {
  const factory ShortBowSymptom({
    required int id,
    @JsonKey(name: 'symptom_name') required String symptomName,
    @JsonKey(name: 'created_at') required String createdAt,
    @JsonKey(name: 'updated_at') required String updatedAt,
  }) = _ShortBowSymptom;

  factory ShortBowSymptom.fromJson(Map<String, dynamic> json) =>
      _$ShortBowSymptomFromJson(json);
}

@freezed
class ShortBowSymptomLink with _$ShortBowSymptomLink {
  const factory ShortBowSymptomLink({
    @JsonKey(name: 'from_symptom') required String fromSymptom,
    @JsonKey(name: 'to_symptom') required String toSymptom,
    required double probability,
  }) = _ShortBowSymptomLink;

  factory ShortBowSymptomLink.fromJson(Map<String, dynamic> json) =>
      _$ShortBowSymptomLinkFromJson(json);
}

@freezed
class ShortBowNavigationRequest with _$ShortBowNavigationRequest {
  const factory ShortBowNavigationRequest({
    @JsonKey(name: 'current_symptom') required String currentSymptom,
    @Default([]) List<String> exclude,
  }) = _ShortBowNavigationRequest;

  factory ShortBowNavigationRequest.fromJson(Map<String, dynamic> json) =>
      _$ShortBowNavigationRequestFromJson(json);
}

@freezed
class ShortBowNavigationResponse with _$ShortBowNavigationResponse {
  const factory ShortBowNavigationResponse({
    @JsonKey(name: 'current_symptom') required String currentSymptom,
    @JsonKey(name: 'top_linked') required List<ShortBowSymptomLink> topLinked,
    @JsonKey(name: 'excluded_symptoms') required List<String> excludedSymptoms,
    @JsonKey(name: 'total_available') required int totalAvailable,
  }) = _ShortBowNavigationResponse;

  factory ShortBowNavigationResponse.fromJson(Map<String, dynamic> json) =>
      _$ShortBowNavigationResponseFromJson(json);
}

@freezed
class ShortBowCalculation with _$ShortBowCalculation {
  const factory ShortBowCalculation({
    required int id,
    @JsonKey(name: 'calculation_date') required String calculationDate,
    @JsonKey(name: 'initial_symptom') required String initialSymptom,
    @JsonKey(name: 'selected_symptoms') required List<String> selectedSymptoms,
    required bool saved,
    @JsonKey(name: 'created_at') required String createdAt,
  }) = _ShortBowCalculation;

  factory ShortBowCalculation.fromJson(Map<String, dynamic> json) =>
      _$ShortBowCalculationFromJson(json);
}

@freezed
class ShortBowCalculationRequest with _$ShortBowCalculationRequest {
  const factory ShortBowCalculationRequest({
    @JsonKey(name: 'initial_symptom') required String initialSymptom,
    @JsonKey(name: 'selected_symptoms') required List<String> selectedSymptoms,
  }) = _ShortBowCalculationRequest;

  factory ShortBowCalculationRequest.fromJson(Map<String, dynamic> json) =>
      _$ShortBowCalculationRequestFromJson(json);
}

@freezed
class ShortBowStats with _$ShortBowStats {
  const factory ShortBowStats({
    @JsonKey(name: 'total_symptoms') required int totalSymptoms,
    @JsonKey(name: 'total_links') required int totalLinks,
    @JsonKey(name: 'total_calculations') required int totalCalculations,
    @JsonKey(name: 'saved_calculations') required int savedCalculations,
  }) = _ShortBowStats;

  factory ShortBowStats.fromJson(Map<String, dynamic> json) =>
      _$ShortBowStatsFromJson(json);
}

@freezed
class ShortBowImportResult with _$ShortBowImportResult {
  const factory ShortBowImportResult({
    required bool success,
    @JsonKey(name: 'symptoms_processed') required int symptomsProcessed,
    @JsonKey(name: 'symptoms_created') required int symptomsCreated,
    @JsonKey(name: 'symptoms_updated') required int symptomsUpdated,
    @JsonKey(name: 'links_processed') required int linksProcessed,
    @JsonKey(name: 'links_created') required int linksCreated,
    @JsonKey(name: 'links_updated') required int linksUpdated,
    required List<String> errors,
    required List<String> warnings,
  }) = _ShortBowImportResult;

  factory ShortBowImportResult.fromJson(Map<String, dynamic> json) =>
      _$ShortBowImportResultFromJson(json);
}
