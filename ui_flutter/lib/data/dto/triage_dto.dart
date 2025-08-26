import 'package:freezed_annotation/freezed_annotation.dart';

part 'triage_dto.freezed.dart';
part 'triage_dto.g.dart';

@freezed
class TriageDTO with _$TriageDTO {
  const factory TriageDTO({
    String? diagnostic_triage,
    String? actions,
  }) = _TriageDTO;

  factory TriageDTO.fromJson(Map<String, dynamic> json) =>
      _$TriageDTOFromJson(json);
}
