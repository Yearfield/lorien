// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'triage_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

TriageDTO _$TriageDTOFromJson(Map<String, dynamic> json) {
  return _TriageDTO.fromJson(json);
}

/// @nodoc
mixin _$TriageDTO {
  @JsonKey(name: 'diagnostic_triage')
  String? get diagnosticTriage => throw _privateConstructorUsedError;
  String? get actions => throw _privateConstructorUsedError;

  /// Serializes this TriageDTO to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of TriageDTO
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $TriageDTOCopyWith<TriageDTO> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TriageDTOCopyWith<$Res> {
  factory $TriageDTOCopyWith(TriageDTO value, $Res Function(TriageDTO) then) =
      _$TriageDTOCopyWithImpl<$Res, TriageDTO>;
  @useResult
  $Res call(
      {@JsonKey(name: 'diagnostic_triage') String? diagnosticTriage,
      String? actions});
}

/// @nodoc
class _$TriageDTOCopyWithImpl<$Res, $Val extends TriageDTO>
    implements $TriageDTOCopyWith<$Res> {
  _$TriageDTOCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of TriageDTO
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? diagnosticTriage = freezed,
    Object? actions = freezed,
  }) {
    return _then(_value.copyWith(
      diagnosticTriage: freezed == diagnosticTriage
          ? _value.diagnosticTriage
          : diagnosticTriage // ignore: cast_nullable_to_non_nullable
              as String?,
      actions: freezed == actions
          ? _value.actions
          : actions // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$TriageDTOImplCopyWith<$Res>
    implements $TriageDTOCopyWith<$Res> {
  factory _$$TriageDTOImplCopyWith(
          _$TriageDTOImpl value, $Res Function(_$TriageDTOImpl) then) =
      __$$TriageDTOImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'diagnostic_triage') String? diagnosticTriage,
      String? actions});
}

/// @nodoc
class __$$TriageDTOImplCopyWithImpl<$Res>
    extends _$TriageDTOCopyWithImpl<$Res, _$TriageDTOImpl>
    implements _$$TriageDTOImplCopyWith<$Res> {
  __$$TriageDTOImplCopyWithImpl(
      _$TriageDTOImpl _value, $Res Function(_$TriageDTOImpl) _then)
      : super(_value, _then);

  /// Create a copy of TriageDTO
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? diagnosticTriage = freezed,
    Object? actions = freezed,
  }) {
    return _then(_$TriageDTOImpl(
      diagnosticTriage: freezed == diagnosticTriage
          ? _value.diagnosticTriage
          : diagnosticTriage // ignore: cast_nullable_to_non_nullable
              as String?,
      actions: freezed == actions
          ? _value.actions
          : actions // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$TriageDTOImpl implements _TriageDTO {
  const _$TriageDTOImpl(
      {@JsonKey(name: 'diagnostic_triage') this.diagnosticTriage,
      this.actions});

  factory _$TriageDTOImpl.fromJson(Map<String, dynamic> json) =>
      _$$TriageDTOImplFromJson(json);

  @override
  @JsonKey(name: 'diagnostic_triage')
  final String? diagnosticTriage;
  @override
  final String? actions;

  @override
  String toString() {
    return 'TriageDTO(diagnosticTriage: $diagnosticTriage, actions: $actions)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TriageDTOImpl &&
            (identical(other.diagnosticTriage, diagnosticTriage) ||
                other.diagnosticTriage == diagnosticTriage) &&
            (identical(other.actions, actions) || other.actions == actions));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, diagnosticTriage, actions);

  /// Create a copy of TriageDTO
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$TriageDTOImplCopyWith<_$TriageDTOImpl> get copyWith =>
      __$$TriageDTOImplCopyWithImpl<_$TriageDTOImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$TriageDTOImplToJson(
      this,
    );
  }
}

abstract class _TriageDTO implements TriageDTO {
  const factory _TriageDTO(
      {@JsonKey(name: 'diagnostic_triage') final String? diagnosticTriage,
      final String? actions}) = _$TriageDTOImpl;

  factory _TriageDTO.fromJson(Map<String, dynamic> json) =
      _$TriageDTOImpl.fromJson;

  @override
  @JsonKey(name: 'diagnostic_triage')
  String? get diagnosticTriage;
  @override
  String? get actions;

  /// Create a copy of TriageDTO
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$TriageDTOImplCopyWith<_$TriageDTOImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
