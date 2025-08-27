// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'incomplete_parent_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$IncompleteParentDTOImpl _$$IncompleteParentDTOImplFromJson(
        Map<String, dynamic> json) =>
    _$IncompleteParentDTOImpl(
      parentId: (json['parentId'] as num).toInt(),
      missingSlots: const _SlotsConverter().fromJson(json['missingSlots']),
    );

Map<String, dynamic> _$$IncompleteParentDTOImplToJson(
        _$IncompleteParentDTOImpl instance) =>
    <String, dynamic>{
      'parentId': instance.parentId,
      'missingSlots': const _SlotsConverter().toJson(instance.missingSlots),
    };
