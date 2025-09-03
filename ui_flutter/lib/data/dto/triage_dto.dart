import 'package:freezed_annotation/freezed_annotation.dart';

part 'triage_dto.freezed.dart';
part 'triage_dto.g.dart';

@freezed
class TriageDTO with _$TriageDTO {
  const factory TriageDTO({
    @JsonKey(name: 'diagnostic_triage') String? diagnosticTriage,
    String? actions,
  }) = _TriageDTO;

  factory TriageDTO.fromJson(Map<String, dynamic> json) =>
      _$TriageDTOFromJson(json);
}
