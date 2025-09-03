// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'triage_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$TriageDTOImpl _$$TriageDTOImplFromJson(Map<String, dynamic> json) =>
    _$TriageDTOImpl(
      diagnosticTriage: json['diagnostic_triage'] as String?,
      actions: json['actions'] as String?,
    );

Map<String, dynamic> _$$TriageDTOImplToJson(_$TriageDTOImpl instance) =>
    <String, dynamic>{
      'diagnostic_triage': instance.diagnosticTriage,
      'actions': instance.actions,
    };
