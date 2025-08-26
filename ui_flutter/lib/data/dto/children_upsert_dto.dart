import 'package:freezed_annotation/freezed_annotation.dart';
import 'child_slot_dto.dart';

part 'children_upsert_dto.freezed.dart';
part 'children_upsert_dto.g.dart';

@freezed
class ChildrenUpsertDTO with _$ChildrenUpsertDTO {
  const factory ChildrenUpsertDTO({
    required List<ChildSlotDTO> children,
  }) = _ChildrenUpsertDTO;

  factory ChildrenUpsertDTO.fromJson(Map<String, dynamic> json) =>
      _$ChildrenUpsertDTOFromJson(json);
}
