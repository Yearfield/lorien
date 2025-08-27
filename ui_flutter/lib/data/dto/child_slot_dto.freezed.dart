// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'child_slot_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

ChildSlotDTO _$ChildSlotDTOFromJson(Map<String, dynamic> json) {
  return _ChildSlotDTO.fromJson(json);
}

/// @nodoc
mixin _$ChildSlotDTO {
  int get slot => throw _privateConstructorUsedError;
  String get label => throw _privateConstructorUsedError;

  /// Serializes this ChildSlotDTO to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ChildSlotDTO
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ChildSlotDTOCopyWith<ChildSlotDTO> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ChildSlotDTOCopyWith<$Res> {
  factory $ChildSlotDTOCopyWith(
          ChildSlotDTO value, $Res Function(ChildSlotDTO) then) =
      _$ChildSlotDTOCopyWithImpl<$Res, ChildSlotDTO>;
  @useResult
  $Res call({int slot, String label});
}

/// @nodoc
class _$ChildSlotDTOCopyWithImpl<$Res, $Val extends ChildSlotDTO>
    implements $ChildSlotDTOCopyWith<$Res> {
  _$ChildSlotDTOCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ChildSlotDTO
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? slot = null,
    Object? label = null,
  }) {
    return _then(_value.copyWith(
      slot: null == slot
          ? _value.slot
          : slot // ignore: cast_nullable_to_non_nullable
              as int,
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ChildSlotDTOImplCopyWith<$Res>
    implements $ChildSlotDTOCopyWith<$Res> {
  factory _$$ChildSlotDTOImplCopyWith(
          _$ChildSlotDTOImpl value, $Res Function(_$ChildSlotDTOImpl) then) =
      __$$ChildSlotDTOImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({int slot, String label});
}

/// @nodoc
class __$$ChildSlotDTOImplCopyWithImpl<$Res>
    extends _$ChildSlotDTOCopyWithImpl<$Res, _$ChildSlotDTOImpl>
    implements _$$ChildSlotDTOImplCopyWith<$Res> {
  __$$ChildSlotDTOImplCopyWithImpl(
      _$ChildSlotDTOImpl _value, $Res Function(_$ChildSlotDTOImpl) _then)
      : super(_value, _then);

  /// Create a copy of ChildSlotDTO
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? slot = null,
    Object? label = null,
  }) {
    return _then(_$ChildSlotDTOImpl(
      slot: null == slot
          ? _value.slot
          : slot // ignore: cast_nullable_to_non_nullable
              as int,
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ChildSlotDTOImpl implements _ChildSlotDTO {
  const _$ChildSlotDTOImpl({required this.slot, required this.label});

  factory _$ChildSlotDTOImpl.fromJson(Map<String, dynamic> json) =>
      _$$ChildSlotDTOImplFromJson(json);

  @override
  final int slot;
  @override
  final String label;

  @override
  String toString() {
    return 'ChildSlotDTO(slot: $slot, label: $label)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ChildSlotDTOImpl &&
            (identical(other.slot, slot) || other.slot == slot) &&
            (identical(other.label, label) || other.label == label));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, slot, label);

  /// Create a copy of ChildSlotDTO
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ChildSlotDTOImplCopyWith<_$ChildSlotDTOImpl> get copyWith =>
      __$$ChildSlotDTOImplCopyWithImpl<_$ChildSlotDTOImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ChildSlotDTOImplToJson(
      this,
    );
  }
}

abstract class _ChildSlotDTO implements ChildSlotDTO {
  const factory _ChildSlotDTO(
      {required final int slot,
      required final String label}) = _$ChildSlotDTOImpl;

  factory _ChildSlotDTO.fromJson(Map<String, dynamic> json) =
      _$ChildSlotDTOImpl.fromJson;

  @override
  int get slot;
  @override
  String get label;

  /// Create a copy of ChildSlotDTO
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ChildSlotDTOImplCopyWith<_$ChildSlotDTOImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
