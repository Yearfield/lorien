import 'package:freezed_annotation/freezed_annotation.dart';

part 'incomplete_parent_dto.freezed.dart';
part 'incomplete_parent_dto.g.dart';

@freezed
class IncompleteParentDTO with _$IncompleteParentDTO {
  const factory IncompleteParentDTO({
    required int parent_id,
    required List<int> missing_slots,
  }) = _IncompleteParentDTO;

  factory IncompleteParentDTO.fromJson(Map<String, dynamic> json) =>
      _$IncompleteParentDTOFromJson(json);
}
