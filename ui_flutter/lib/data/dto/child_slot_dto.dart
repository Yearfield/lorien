import 'package:freezed_annotation/freezed_annotation.dart';

part 'child_slot_dto.freezed.dart';
part 'child_slot_dto.g.dart';

@freezed
class ChildSlotDTO with _$ChildSlotDTO {
  const factory ChildSlotDTO({
    required int slot,
    required String label,
  }) = _ChildSlotDTO;

  factory ChildSlotDTO.fromJson(Map<String, dynamic> json) =>
      _$ChildSlotDTOFromJson(json);
}
