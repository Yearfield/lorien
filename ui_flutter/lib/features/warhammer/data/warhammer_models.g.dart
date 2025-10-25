// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'warhammer_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$SymptomImpl _$$SymptomImplFromJson(Map<String, dynamic> json) =>
    _$SymptomImpl(
      id: (json['id'] as num).toInt(),
      symptomName: json['symptom_name'] as String,
      probability: (json['probability'] as num).toDouble(),
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
    );

Map<String, dynamic> _$$SymptomImplToJson(_$SymptomImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'symptom_name': instance.symptomName,
      'probability': instance.probability,
      'created_at': instance.createdAt,
      'updated_at': instance.updatedAt,
    };

_$DiseaseImpl _$$DiseaseImplFromJson(Map<String, dynamic> json) =>
    _$DiseaseImpl(
      id: (json['id'] as num).toInt(),
      diseaseName: json['disease_name'] as String,
      estimatedLifetimeRisk:
          (json['estimated_lifetime_risk'] as num).toDouble(),
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
    );

Map<String, dynamic> _$$DiseaseImplToJson(_$DiseaseImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'disease_name': instance.diseaseName,
      'estimated_lifetime_risk': instance.estimatedLifetimeRisk,
      'created_at': instance.createdAt,
      'updated_at': instance.updatedAt,
    };

_$DiseaseResultImpl _$$DiseaseResultImplFromJson(Map<String, dynamic> json) =>
    _$DiseaseResultImpl(
      disease: json['disease'] as String,
      probability: (json['probability'] as num).toDouble(),
    );

Map<String, dynamic> _$$DiseaseResultImplToJson(_$DiseaseResultImpl instance) =>
    <String, dynamic>{
      'disease': instance.disease,
      'probability': instance.probability,
    };

_$CalculationRequestImpl _$$CalculationRequestImplFromJson(
        Map<String, dynamic> json) =>
    _$CalculationRequestImpl(
      symptoms:
          (json['symptoms'] as List<dynamic>).map((e) => e as String).toList(),
    );

Map<String, dynamic> _$$CalculationRequestImplToJson(
        _$CalculationRequestImpl instance) =>
    <String, dynamic>{
      'symptoms': instance.symptoms,
    };

_$CalculationResponseImpl _$$CalculationResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$CalculationResponseImpl(
      calculationId: (json['calculationId'] as num?)?.toInt(),
      inputSymptoms: (json['inputSymptoms'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      results: (json['results'] as List<dynamic>)
          .map((e) => DiseaseResult.fromJson(e as Map<String, dynamic>))
          .toList(),
      timestamp: json['timestamp'] as String,
      errors: (json['errors'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$CalculationResponseImplToJson(
        _$CalculationResponseImpl instance) =>
    <String, dynamic>{
      'calculationId': instance.calculationId,
      'inputSymptoms': instance.inputSymptoms,
      'results': instance.results,
      'timestamp': instance.timestamp,
      'errors': instance.errors,
    };

_$ImportResultResponseImpl _$$ImportResultResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$ImportResultResponseImpl(
      success: json['success'] as bool,
      diseasesProcessed: (json['diseasesProcessed'] as num?)?.toInt() ?? 0,
      diseasesCreated: (json['diseasesCreated'] as num?)?.toInt() ?? 0,
      diseasesUpdated: (json['diseasesUpdated'] as num?)?.toInt() ?? 0,
      symptomsProcessed: (json['symptomsProcessed'] as num?)?.toInt() ?? 0,
      symptomsCreated: (json['symptomsCreated'] as num?)?.toInt() ?? 0,
      symptomsUpdated: (json['symptomsUpdated'] as num?)?.toInt() ?? 0,
      conditionalsProcessed:
          (json['conditionalsProcessed'] as num?)?.toInt() ?? 0,
      conditionalsCreated: (json['conditionalsCreated'] as num?)?.toInt() ?? 0,
      conditionalsUpdated: (json['conditionalsUpdated'] as num?)?.toInt() ?? 0,
      errors: (json['errors'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      warnings: (json['warnings'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$ImportResultResponseImplToJson(
        _$ImportResultResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'diseasesProcessed': instance.diseasesProcessed,
      'diseasesCreated': instance.diseasesCreated,
      'diseasesUpdated': instance.diseasesUpdated,
      'symptomsProcessed': instance.symptomsProcessed,
      'symptomsCreated': instance.symptomsCreated,
      'symptomsUpdated': instance.symptomsUpdated,
      'conditionalsProcessed': instance.conditionalsProcessed,
      'conditionalsCreated': instance.conditionalsCreated,
      'conditionalsUpdated': instance.conditionalsUpdated,
      'errors': instance.errors,
      'warnings': instance.warnings,
    };

_$WarhammerStatsImpl _$$WarhammerStatsImplFromJson(Map<String, dynamic> json) =>
    _$WarhammerStatsImpl(
      totalDiseases: (json['total_diseases'] as num).toInt(),
      totalSymptoms: (json['total_symptoms'] as num).toInt(),
      totalConditionals: (json['total_conditionals'] as num).toInt(),
      totalCalculations: (json['total_calculations'] as num).toInt(),
      savedCalculations: (json['saved_calculations'] as num).toInt(),
    );

Map<String, dynamic> _$$WarhammerStatsImplToJson(
        _$WarhammerStatsImpl instance) =>
    <String, dynamic>{
      'total_diseases': instance.totalDiseases,
      'total_symptoms': instance.totalSymptoms,
      'total_conditionals': instance.totalConditionals,
      'total_calculations': instance.totalCalculations,
      'saved_calculations': instance.savedCalculations,
    };

_$SavedCalculationImpl _$$SavedCalculationImplFromJson(
        Map<String, dynamic> json) =>
    _$SavedCalculationImpl(
      id: (json['id'] as num).toInt(),
      calculationDate: json['calculationDate'] as String,
      inputSymptoms: (json['inputSymptoms'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      results: (json['results'] as List<dynamic>)
          .map((e) => DiseaseResult.fromJson(e as Map<String, dynamic>))
          .toList(),
      saved: json['saved'] as bool,
    );

Map<String, dynamic> _$$SavedCalculationImplToJson(
        _$SavedCalculationImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'calculationDate': instance.calculationDate,
      'inputSymptoms': instance.inputSymptoms,
      'results': instance.results,
      'saved': instance.saved,
    };

_$NormalizedMatchImpl _$$NormalizedMatchImplFromJson(
        Map<String, dynamic> json) =>
    _$NormalizedMatchImpl(
      decisionTree: json['decision_tree'] as String,
      warhammer: json['warhammer'] as String,
      normalized: json['normalized'] as String,
    );

Map<String, dynamic> _$$NormalizedMatchImplToJson(
        _$NormalizedMatchImpl instance) =>
    <String, dynamic>{
      'decision_tree': instance.decisionTree,
      'warhammer': instance.warhammer,
      'normalized': instance.normalized,
    };

_$SymptomSynonymImpl _$$SymptomSynonymImplFromJson(Map<String, dynamic> json) =>
    _$SymptomSynonymImpl(
      id: (json['id'] as num).toInt(),
      warhammerSymptom: json['warhammer_symptom'] as String,
      decisionTreeSymptom: json['decision_tree_symptom'] as String,
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
    );

Map<String, dynamic> _$$SymptomSynonymImplToJson(
        _$SymptomSynonymImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'warhammer_symptom': instance.warhammerSymptom,
      'decision_tree_symptom': instance.decisionTreeSymptom,
      'created_at': instance.createdAt,
      'updated_at': instance.updatedAt,
    };

_$CreateSynonymRequestImpl _$$CreateSynonymRequestImplFromJson(
        Map<String, dynamic> json) =>
    _$CreateSynonymRequestImpl(
      warhammerSymptom: json['warhammer_symptom'] as String,
      decisionTreeSymptom: json['decision_tree_symptom'] as String,
    );

Map<String, dynamic> _$$CreateSynonymRequestImplToJson(
        _$CreateSynonymRequestImpl instance) =>
    <String, dynamic>{
      'warhammer_symptom': instance.warhammerSymptom,
      'decision_tree_symptom': instance.decisionTreeSymptom,
    };

_$SymptomComparisonImpl _$$SymptomComparisonImplFromJson(
        Map<String, dynamic> json) =>
    _$SymptomComparisonImpl(
      decisionTreeSymptoms: (json['decision_tree_symptoms'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      warhammerSymptoms: (json['warhammer_symptoms'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      matchingSymptoms: (json['matching_symptoms'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      missingFromWarhammer: (json['missing_from_warhammer'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      extraInWarhammer: (json['extra_in_warhammer'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      totalDecisionTree: (json['total_decision_tree'] as num?)?.toInt() ?? 0,
      totalWarhammer: (json['total_warhammer'] as num?)?.toInt() ?? 0,
      matchCount: (json['match_count'] as num?)?.toInt() ?? 0,
      normalizedMatches: (json['normalized_matches'] as List<dynamic>?)
              ?.map((e) => NormalizedMatch.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$SymptomComparisonImplToJson(
        _$SymptomComparisonImpl instance) =>
    <String, dynamic>{
      'decision_tree_symptoms': instance.decisionTreeSymptoms,
      'warhammer_symptoms': instance.warhammerSymptoms,
      'matching_symptoms': instance.matchingSymptoms,
      'missing_from_warhammer': instance.missingFromWarhammer,
      'extra_in_warhammer': instance.extraInWarhammer,
      'total_decision_tree': instance.totalDecisionTree,
      'total_warhammer': instance.totalWarhammer,
      'match_count': instance.matchCount,
      'normalized_matches': instance.normalizedMatches,
    };
