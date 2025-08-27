import 'package:freezed_annotation/freezed_annotation.dart';

part 'incomplete_parent_dto.freezed.dart';
part 'incomplete_parent_dto.g.dart';

class _SlotsConverter implements JsonConverter<List<int>, Object?> {
  const _SlotsConverter();
  @override
  List<int> fromJson(Object? json) {
    if (json == null) return const <int>[];
    if (json is List) {
      return json.map((e) {
        if (e is int) return e;
        if (e is num) return e.toInt();
        if (e is String) return int.tryParse(e.trim()) ?? 0;
        return 0;
      }).where((v) => v > 0).toList();
    }
    if (json is String) {
      return json
          .split(',')
          .map((s) => int.tryParse(s.trim()) ?? 0)
          .where((v) => v > 0)
          .toList();
    }
    return const <int>[];
  }
  @override
  Object toJson(List<int> object) => object; // encode back as JSON array
}

@freezed
class IncompleteParentDTO with _$IncompleteParentDTO {
  const factory IncompleteParentDTO({
    required int parentId,
    @_SlotsConverter() required List<int> missingSlots,
  }) = _IncompleteParentDTO;

  factory IncompleteParentDTO.fromJson(Map<String, dynamic> json) =>
      _$IncompleteParentDTOFromJson(json);
}
