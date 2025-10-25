// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'shortbow_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ShortBowSymptomImpl _$$ShortBowSymptomImplFromJson(
        Map<String, dynamic> json) =>
    _$ShortBowSymptomImpl(
      id: (json['id'] as num).toInt(),
      symptomName: json['symptom_name'] as String,
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
    );

Map<String, dynamic> _$$ShortBowSymptomImplToJson(
        _$ShortBowSymptomImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'symptom_name': instance.symptomName,
      'created_at': instance.createdAt,
      'updated_at': instance.updatedAt,
    };

_$ShortBowSymptomLinkImpl _$$ShortBowSymptomLinkImplFromJson(
        Map<String, dynamic> json) =>
    _$ShortBowSymptomLinkImpl(
      fromSymptom: json['from_symptom'] as String,
      toSymptom: json['to_symptom'] as String,
      probability: (json['probability'] as num).toDouble(),
    );

Map<String, dynamic> _$$ShortBowSymptomLinkImplToJson(
        _$ShortBowSymptomLinkImpl instance) =>
    <String, dynamic>{
      'from_symptom': instance.fromSymptom,
      'to_symptom': instance.toSymptom,
      'probability': instance.probability,
    };

_$ShortBowNavigationRequestImpl _$$ShortBowNavigationRequestImplFromJson(
        Map<String, dynamic> json) =>
    _$ShortBowNavigationRequestImpl(
      currentSymptom: json['current_symptom'] as String,
      exclude: (json['exclude'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$ShortBowNavigationRequestImplToJson(
        _$ShortBowNavigationRequestImpl instance) =>
    <String, dynamic>{
      'current_symptom': instance.currentSymptom,
      'exclude': instance.exclude,
    };

_$ShortBowNavigationResponseImpl _$$ShortBowNavigationResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$ShortBowNavigationResponseImpl(
      currentSymptom: json['current_symptom'] as String,
      topLinked: (json['top_linked'] as List<dynamic>)
          .map((e) => ShortBowSymptomLink.fromJson(e as Map<String, dynamic>))
          .toList(),
      excludedSymptoms: (json['excluded_symptoms'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      totalAvailable: (json['total_available'] as num).toInt(),
    );

Map<String, dynamic> _$$ShortBowNavigationResponseImplToJson(
        _$ShortBowNavigationResponseImpl instance) =>
    <String, dynamic>{
      'current_symptom': instance.currentSymptom,
      'top_linked': instance.topLinked,
      'excluded_symptoms': instance.excludedSymptoms,
      'total_available': instance.totalAvailable,
    };

_$ShortBowCalculationImpl _$$ShortBowCalculationImplFromJson(
        Map<String, dynamic> json) =>
    _$ShortBowCalculationImpl(
      id: (json['id'] as num).toInt(),
      calculationDate: json['calculation_date'] as String,
      initialSymptom: json['initial_symptom'] as String,
      selectedSymptoms: (json['selected_symptoms'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      saved: json['saved'] as bool,
      createdAt: json['created_at'] as String,
    );

Map<String, dynamic> _$$ShortBowCalculationImplToJson(
        _$ShortBowCalculationImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'calculation_date': instance.calculationDate,
      'initial_symptom': instance.initialSymptom,
      'selected_symptoms': instance.selectedSymptoms,
      'saved': instance.saved,
      'created_at': instance.createdAt,
    };

_$ShortBowCalculationRequestImpl _$$ShortBowCalculationRequestImplFromJson(
        Map<String, dynamic> json) =>
    _$ShortBowCalculationRequestImpl(
      initialSymptom: json['initial_symptom'] as String,
      selectedSymptoms: (json['selected_symptoms'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
    );

Map<String, dynamic> _$$ShortBowCalculationRequestImplToJson(
        _$ShortBowCalculationRequestImpl instance) =>
    <String, dynamic>{
      'initial_symptom': instance.initialSymptom,
      'selected_symptoms': instance.selectedSymptoms,
    };

_$ShortBowStatsImpl _$$ShortBowStatsImplFromJson(Map<String, dynamic> json) =>
    _$ShortBowStatsImpl(
      totalSymptoms: (json['total_symptoms'] as num).toInt(),
      totalLinks: (json['total_links'] as num).toInt(),
      totalCalculations: (json['total_calculations'] as num).toInt(),
      savedCalculations: (json['saved_calculations'] as num).toInt(),
    );

Map<String, dynamic> _$$ShortBowStatsImplToJson(_$ShortBowStatsImpl instance) =>
    <String, dynamic>{
      'total_symptoms': instance.totalSymptoms,
      'total_links': instance.totalLinks,
      'total_calculations': instance.totalCalculations,
      'saved_calculations': instance.savedCalculations,
    };

_$ShortBowImportResultImpl _$$ShortBowImportResultImplFromJson(
        Map<String, dynamic> json) =>
    _$ShortBowImportResultImpl(
      success: json['success'] as bool,
      symptomsProcessed: (json['symptoms_processed'] as num).toInt(),
      symptomsCreated: (json['symptoms_created'] as num).toInt(),
      symptomsUpdated: (json['symptoms_updated'] as num).toInt(),
      linksProcessed: (json['links_processed'] as num).toInt(),
      linksCreated: (json['links_created'] as num).toInt(),
      linksUpdated: (json['links_updated'] as num).toInt(),
      errors:
          (json['errors'] as List<dynamic>).map((e) => e as String).toList(),
      warnings:
          (json['warnings'] as List<dynamic>).map((e) => e as String).toList(),
    );

Map<String, dynamic> _$$ShortBowImportResultImplToJson(
        _$ShortBowImportResultImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'symptoms_processed': instance.symptomsProcessed,
      'symptoms_created': instance.symptomsCreated,
      'symptoms_updated': instance.symptomsUpdated,
      'links_processed': instance.linksProcessed,
      'links_created': instance.linksCreated,
      'links_updated': instance.linksUpdated,
      'errors': instance.errors,
      'warnings': instance.warnings,
    };
