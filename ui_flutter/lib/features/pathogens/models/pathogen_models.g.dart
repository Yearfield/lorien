// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pathogen_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$PathogenImpl _$$PathogenImplFromJson(Map<String, dynamic> json) =>
    _$PathogenImpl(
      id: (json['id'] as num).toInt(),
      classification: json['classification'] as String?,
      nt: json['nt'] as String?,
      pathogenId: json['pathogen_id'] as String?,
      pathogenName: json['pathogen_name'] as String,
      vaccine: json['vaccine'] as String?,
      toxin: json['toxin'] as String?,
      transmission: json['transmission'] as String?,
      abResistance: json['ab_resistance'] as String?,
      host: json['host'] as String?,
      commensal: json['commensal'] as String?,
      disease: json['disease'] as String?,
      incubation: json['incubation'] as String?,
      diagnosis: json['diagnosis'] as String?,
      treatment: json['treatment'] as String?,
      prevention: json['prevention'] as String?,
      notes: json['notes'] as String?,
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
    );

Map<String, dynamic> _$$PathogenImplToJson(_$PathogenImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'classification': instance.classification,
      'nt': instance.nt,
      'pathogen_id': instance.pathogenId,
      'pathogen_name': instance.pathogenName,
      'vaccine': instance.vaccine,
      'toxin': instance.toxin,
      'transmission': instance.transmission,
      'ab_resistance': instance.abResistance,
      'host': instance.host,
      'commensal': instance.commensal,
      'disease': instance.disease,
      'incubation': instance.incubation,
      'diagnosis': instance.diagnosis,
      'treatment': instance.treatment,
      'prevention': instance.prevention,
      'notes': instance.notes,
      'created_at': instance.createdAt,
      'updated_at': instance.updatedAt,
    };

_$AssociationTypeImpl _$$AssociationTypeImplFromJson(
        Map<String, dynamic> json) =>
    _$AssociationTypeImpl(
      id: (json['id'] as num).toInt(),
      name: json['name'] as String,
      description: json['description'] as String?,
      createdAt: json['created_at'] as String,
    );

Map<String, dynamic> _$$AssociationTypeImplToJson(
        _$AssociationTypeImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'created_at': instance.createdAt,
    };

_$PathogenAssociationImpl _$$PathogenAssociationImplFromJson(
        Map<String, dynamic> json) =>
    _$PathogenAssociationImpl(
      pathogenId: (json['pathogen_id'] as num).toInt(),
      associationTypeId: (json['association_type_id'] as num).toInt(),
      value: (json['value'] as num).toInt(),
      associationTypeName: json['association_type_name'] as String?,
    );

Map<String, dynamic> _$$PathogenAssociationImplToJson(
        _$PathogenAssociationImpl instance) =>
    <String, dynamic>{
      'pathogen_id': instance.pathogenId,
      'association_type_id': instance.associationTypeId,
      'value': instance.value,
      'association_type_name': instance.associationTypeName,
    };

_$PathogenWithAssociationsImpl _$$PathogenWithAssociationsImplFromJson(
        Map<String, dynamic> json) =>
    _$PathogenWithAssociationsImpl(
      id: (json['id'] as num).toInt(),
      classification: json['classification'] as String?,
      nt: json['nt'] as String?,
      pathogenId: json['pathogen_id'] as String?,
      pathogenName: json['pathogen_name'] as String,
      vaccine: json['vaccine'] as String?,
      toxin: json['toxin'] as String?,
      transmission: json['transmission'] as String?,
      abResistance: json['ab_resistance'] as String?,
      host: json['host'] as String?,
      commensal: json['commensal'] as String?,
      disease: json['disease'] as String?,
      incubation: json['incubation'] as String?,
      diagnosis: json['diagnosis'] as String?,
      treatment: json['treatment'] as String?,
      prevention: json['prevention'] as String?,
      notes: json['notes'] as String?,
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
      associations: (json['associations'] as List<dynamic>)
          .map((e) => PathogenAssociation.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$$PathogenWithAssociationsImplToJson(
        _$PathogenWithAssociationsImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'classification': instance.classification,
      'nt': instance.nt,
      'pathogen_id': instance.pathogenId,
      'pathogen_name': instance.pathogenName,
      'vaccine': instance.vaccine,
      'toxin': instance.toxin,
      'transmission': instance.transmission,
      'ab_resistance': instance.abResistance,
      'host': instance.host,
      'commensal': instance.commensal,
      'disease': instance.disease,
      'incubation': instance.incubation,
      'diagnosis': instance.diagnosis,
      'treatment': instance.treatment,
      'prevention': instance.prevention,
      'notes': instance.notes,
      'created_at': instance.createdAt,
      'updated_at': instance.updatedAt,
      'associations': instance.associations,
    };

_$PathogenStatsImpl _$$PathogenStatsImplFromJson(Map<String, dynamic> json) =>
    _$PathogenStatsImpl(
      totalPathogens: (json['total_pathogens'] as num).toInt(),
      totalAssociations: (json['total_associations'] as num).toInt(),
      pathogensWithAssociations:
          (json['pathogens_with_associations'] as num).toInt(),
      averageAssociationsPerPathogen:
          (json['average_associations_per_pathogen'] as num).toDouble(),
    );

Map<String, dynamic> _$$PathogenStatsImplToJson(_$PathogenStatsImpl instance) =>
    <String, dynamic>{
      'total_pathogens': instance.totalPathogens,
      'total_associations': instance.totalAssociations,
      'pathogens_with_associations': instance.pathogensWithAssociations,
      'average_associations_per_pathogen':
          instance.averageAssociationsPerPathogen,
    };

_$PathogenImportResultImpl _$$PathogenImportResultImplFromJson(
        Map<String, dynamic> json) =>
    _$PathogenImportResultImpl(
      success: json['success'] as bool,
      pathogensProcessed: (json['pathogens_processed'] as num).toInt(),
      pathogensCreated: (json['pathogens_created'] as num).toInt(),
      pathogensUpdated: (json['pathogens_updated'] as num).toInt(),
      associationsProcessed: (json['associations_processed'] as num).toInt(),
      associationsCreated: (json['associations_created'] as num).toInt(),
      errors:
          (json['errors'] as List<dynamic>).map((e) => e as String).toList(),
      warnings:
          (json['warnings'] as List<dynamic>).map((e) => e as String).toList(),
    );

Map<String, dynamic> _$$PathogenImportResultImplToJson(
        _$PathogenImportResultImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'pathogens_processed': instance.pathogensProcessed,
      'pathogens_created': instance.pathogensCreated,
      'pathogens_updated': instance.pathogensUpdated,
      'associations_processed': instance.associationsProcessed,
      'associations_created': instance.associationsCreated,
      'errors': instance.errors,
      'warnings': instance.warnings,
    };

_$PathogenPropertiesImpl _$$PathogenPropertiesImplFromJson(
        Map<String, dynamic> json) =>
    _$PathogenPropertiesImpl(
      classification: json['classification'] as String?,
      nt: json['nt'] as String?,
      pathogenId: json['pathogen_id'] as String?,
      pathogenName: json['pathogen_name'] as String,
      vaccine: json['vaccine'] as String?,
      toxin: json['toxin'] as String?,
      transmission: json['transmission'] as String?,
      abResistance: json['ab_resistance'] as String?,
      host: json['host'] as String?,
      commensal: json['commensal'] as String?,
      disease: json['disease'] as String?,
      incubation: json['incubation'] as String?,
      diagnosis: json['diagnosis'] as String?,
      treatment: json['treatment'] as String?,
      prevention: json['prevention'] as String?,
      notes: json['notes'] as String?,
    );

Map<String, dynamic> _$$PathogenPropertiesImplToJson(
        _$PathogenPropertiesImpl instance) =>
    <String, dynamic>{
      'classification': instance.classification,
      'nt': instance.nt,
      'pathogen_id': instance.pathogenId,
      'pathogen_name': instance.pathogenName,
      'vaccine': instance.vaccine,
      'toxin': instance.toxin,
      'transmission': instance.transmission,
      'ab_resistance': instance.abResistance,
      'host': instance.host,
      'commensal': instance.commensal,
      'disease': instance.disease,
      'incubation': instance.incubation,
      'diagnosis': instance.diagnosis,
      'treatment': instance.treatment,
      'prevention': instance.prevention,
      'notes': instance.notes,
    };
