import 'package:freezed_annotation/freezed_annotation.dart';

import '../data/warhammer_models.dart';

part 'warhammer_state.freezed.dart';

@freezed
class WarhammerState with _$WarhammerState {
  const factory WarhammerState({
    @Default([]) List<Symptom> symptoms,
    @Default([]) List<Disease> diseases,
    WarhammerStats? stats,
    SymptomComparison? symptomComparison,
    @Default([]) List<SymptomSynonym> synonyms,
    @Default(false) bool isLoading,
    @Default(false) bool isCalculating,
    @Default(false) bool isImporting,
    @Default(false) bool isLoadingComparison,
    @Default(false) bool isLoadingSynonyms,
    String? error,
    @Default([]) List<String> selectedSymptoms,
    CalculationResponse? lastCalculation,
    @Default([]) List<SavedCalculation> savedCalculations,
    @Default(0) int currentParentId,
    @Default([]) List<Map<String, dynamic>> currentTreeOptions,
    @Default([]) List<Map<String, dynamic>> decisionTreeRoots,
  }) = _WarhammerState;
}

@freezed
class WarhammerCalculationState with _$WarhammerCalculationState {
  const factory WarhammerCalculationState({
    @Default([]) List<String> selectedSymptoms,
    CalculationResponse? result,
    @Default(false) bool isCalculating,
    String? error,
  }) = _WarhammerCalculationState;
}

@freezed
class WarhammerImportState with _$WarhammerImportState {
  const factory WarhammerImportState({
    @Default(false) bool isImportingDiseases,
    @Default(false) bool isImportingSymptoms,
    @Default(false) bool isImportingConditionals,
    ImportResultResponse? lastImportResult,
    String? error,
  }) = _WarhammerImportState;
}
