// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'incomplete_parent_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$IncompleteParentDTOImpl _$$IncompleteParentDTOImplFromJson(
        Map<String, dynamic> json) =>
    _$IncompleteParentDTOImpl(
      parentId: (json['parent_id'] as num).toInt(),
      missingSlots: const _SlotsConverter().fromJson(json['missing_slots']),
    );

Map<String, dynamic> _$$IncompleteParentDTOImplToJson(
        _$IncompleteParentDTOImpl instance) =>
    <String, dynamic>{
      'parent_id': instance.parentId,
      'missing_slots': const _SlotsConverter().toJson(instance.missingSlots),
    };
