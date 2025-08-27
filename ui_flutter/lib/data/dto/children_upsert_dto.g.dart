// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'children_upsert_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ChildrenUpsertDTOImpl _$$ChildrenUpsertDTOImplFromJson(
        Map<String, dynamic> json) =>
    _$ChildrenUpsertDTOImpl(
      children: (json['children'] as List<dynamic>)
          .map((e) => ChildSlotDTO.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$$ChildrenUpsertDTOImplToJson(
        _$ChildrenUpsertDTOImpl instance) =>
    <String, dynamic>{
      'children': instance.children,
    };
