// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'children_upsert_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

ChildrenUpsertDTO _$ChildrenUpsertDTOFromJson(Map<String, dynamic> json) {
  return _ChildrenUpsertDTO.fromJson(json);
}

/// @nodoc
mixin _$ChildrenUpsertDTO {
  List<ChildSlotDTO> get children => throw _privateConstructorUsedError;

  /// Serializes this ChildrenUpsertDTO to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ChildrenUpsertDTO
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ChildrenUpsertDTOCopyWith<ChildrenUpsertDTO> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ChildrenUpsertDTOCopyWith<$Res> {
  factory $ChildrenUpsertDTOCopyWith(
          ChildrenUpsertDTO value, $Res Function(ChildrenUpsertDTO) then) =
      _$ChildrenUpsertDTOCopyWithImpl<$Res, ChildrenUpsertDTO>;
  @useResult
  $Res call({List<ChildSlotDTO> children});
}

/// @nodoc
class _$ChildrenUpsertDTOCopyWithImpl<$Res, $Val extends ChildrenUpsertDTO>
    implements $ChildrenUpsertDTOCopyWith<$Res> {
  _$ChildrenUpsertDTOCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ChildrenUpsertDTO
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? children = null,
  }) {
    return _then(_value.copyWith(
      children: null == children
          ? _value.children
          : children // ignore: cast_nullable_to_non_nullable
              as List<ChildSlotDTO>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ChildrenUpsertDTOImplCopyWith<$Res>
    implements $ChildrenUpsertDTOCopyWith<$Res> {
  factory _$$ChildrenUpsertDTOImplCopyWith(_$ChildrenUpsertDTOImpl value,
          $Res Function(_$ChildrenUpsertDTOImpl) then) =
      __$$ChildrenUpsertDTOImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({List<ChildSlotDTO> children});
}

/// @nodoc
class __$$ChildrenUpsertDTOImplCopyWithImpl<$Res>
    extends _$ChildrenUpsertDTOCopyWithImpl<$Res, _$ChildrenUpsertDTOImpl>
    implements _$$ChildrenUpsertDTOImplCopyWith<$Res> {
  __$$ChildrenUpsertDTOImplCopyWithImpl(_$ChildrenUpsertDTOImpl _value,
      $Res Function(_$ChildrenUpsertDTOImpl) _then)
      : super(_value, _then);

  /// Create a copy of ChildrenUpsertDTO
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? children = null,
  }) {
    return _then(_$ChildrenUpsertDTOImpl(
      children: null == children
          ? _value._children
          : children // ignore: cast_nullable_to_non_nullable
              as List<ChildSlotDTO>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ChildrenUpsertDTOImpl implements _ChildrenUpsertDTO {
  const _$ChildrenUpsertDTOImpl({required final List<ChildSlotDTO> children})
      : _children = children;

  factory _$ChildrenUpsertDTOImpl.fromJson(Map<String, dynamic> json) =>
      _$$ChildrenUpsertDTOImplFromJson(json);

  final List<ChildSlotDTO> _children;
  @override
  List<ChildSlotDTO> get children {
    if (_children is EqualUnmodifiableListView) return _children;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_children);
  }

  @override
  String toString() {
    return 'ChildrenUpsertDTO(children: $children)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ChildrenUpsertDTOImpl &&
            const DeepCollectionEquality().equals(other._children, _children));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, const DeepCollectionEquality().hash(_children));

  /// Create a copy of ChildrenUpsertDTO
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ChildrenUpsertDTOImplCopyWith<_$ChildrenUpsertDTOImpl> get copyWith =>
      __$$ChildrenUpsertDTOImplCopyWithImpl<_$ChildrenUpsertDTOImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ChildrenUpsertDTOImplToJson(
      this,
    );
  }
}

abstract class _ChildrenUpsertDTO implements ChildrenUpsertDTO {
  const factory _ChildrenUpsertDTO(
      {required final List<ChildSlotDTO> children}) = _$ChildrenUpsertDTOImpl;

  factory _ChildrenUpsertDTO.fromJson(Map<String, dynamic> json) =
      _$ChildrenUpsertDTOImpl.fromJson;

  @override
  List<ChildSlotDTO> get children;

  /// Create a copy of ChildrenUpsertDTO
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ChildrenUpsertDTOImplCopyWith<_$ChildrenUpsertDTOImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
