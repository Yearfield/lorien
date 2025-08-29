// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'incomplete_parent_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

IncompleteParentDTO _$IncompleteParentDTOFromJson(Map<String, dynamic> json) {
  return _IncompleteParentDTO.fromJson(json);
}

/// @nodoc
mixin _$IncompleteParentDTO {
  @JsonKey(name: 'parent_id')
  int get parentId => throw _privateConstructorUsedError;
  @JsonKey(name: 'missing_slots')
  @_SlotsConverter()
  List<int> get missingSlots => throw _privateConstructorUsedError;

  /// Serializes this IncompleteParentDTO to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of IncompleteParentDTO
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $IncompleteParentDTOCopyWith<IncompleteParentDTO> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IncompleteParentDTOCopyWith<$Res> {
  factory $IncompleteParentDTOCopyWith(
          IncompleteParentDTO value, $Res Function(IncompleteParentDTO) then) =
      _$IncompleteParentDTOCopyWithImpl<$Res, IncompleteParentDTO>;
  @useResult
  $Res call(
      {@JsonKey(name: 'parent_id') int parentId,
      @JsonKey(name: 'missing_slots')
      @_SlotsConverter()
      List<int> missingSlots});
}

/// @nodoc
class _$IncompleteParentDTOCopyWithImpl<$Res, $Val extends IncompleteParentDTO>
    implements $IncompleteParentDTOCopyWith<$Res> {
  _$IncompleteParentDTOCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of IncompleteParentDTO
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? parentId = null,
    Object? missingSlots = null,
  }) {
    return _then(_value.copyWith(
      parentId: null == parentId
          ? _value.parentId
          : parentId // ignore: cast_nullable_to_non_nullable
              as int,
      missingSlots: null == missingSlots
          ? _value.missingSlots
          : missingSlots // ignore: cast_nullable_to_non_nullable
              as List<int>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$IncompleteParentDTOImplCopyWith<$Res>
    implements $IncompleteParentDTOCopyWith<$Res> {
  factory _$$IncompleteParentDTOImplCopyWith(_$IncompleteParentDTOImpl value,
          $Res Function(_$IncompleteParentDTOImpl) then) =
      __$$IncompleteParentDTOImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'parent_id') int parentId,
      @JsonKey(name: 'missing_slots')
      @_SlotsConverter()
      List<int> missingSlots});
}

/// @nodoc
class __$$IncompleteParentDTOImplCopyWithImpl<$Res>
    extends _$IncompleteParentDTOCopyWithImpl<$Res, _$IncompleteParentDTOImpl>
    implements _$$IncompleteParentDTOImplCopyWith<$Res> {
  __$$IncompleteParentDTOImplCopyWithImpl(_$IncompleteParentDTOImpl _value,
      $Res Function(_$IncompleteParentDTOImpl) _then)
      : super(_value, _then);

  /// Create a copy of IncompleteParentDTO
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? parentId = null,
    Object? missingSlots = null,
  }) {
    return _then(_$IncompleteParentDTOImpl(
      parentId: null == parentId
          ? _value.parentId
          : parentId // ignore: cast_nullable_to_non_nullable
              as int,
      missingSlots: null == missingSlots
          ? _value._missingSlots
          : missingSlots // ignore: cast_nullable_to_non_nullable
              as List<int>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$IncompleteParentDTOImpl implements _IncompleteParentDTO {
  const _$IncompleteParentDTOImpl(
      {@JsonKey(name: 'parent_id') required this.parentId,
      @JsonKey(name: 'missing_slots')
      @_SlotsConverter()
      required final List<int> missingSlots})
      : _missingSlots = missingSlots;

  factory _$IncompleteParentDTOImpl.fromJson(Map<String, dynamic> json) =>
      _$$IncompleteParentDTOImplFromJson(json);

  @override
  @JsonKey(name: 'parent_id')
  final int parentId;
  final List<int> _missingSlots;
  @override
  @JsonKey(name: 'missing_slots')
  @_SlotsConverter()
  List<int> get missingSlots {
    if (_missingSlots is EqualUnmodifiableListView) return _missingSlots;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_missingSlots);
  }

  @override
  String toString() {
    return 'IncompleteParentDTO(parentId: $parentId, missingSlots: $missingSlots)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$IncompleteParentDTOImpl &&
            (identical(other.parentId, parentId) ||
                other.parentId == parentId) &&
            const DeepCollectionEquality()
                .equals(other._missingSlots, _missingSlots));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, parentId,
      const DeepCollectionEquality().hash(_missingSlots));

  /// Create a copy of IncompleteParentDTO
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$IncompleteParentDTOImplCopyWith<_$IncompleteParentDTOImpl> get copyWith =>
      __$$IncompleteParentDTOImplCopyWithImpl<_$IncompleteParentDTOImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$IncompleteParentDTOImplToJson(
      this,
    );
  }
}

abstract class _IncompleteParentDTO implements IncompleteParentDTO {
  const factory _IncompleteParentDTO(
      {@JsonKey(name: 'parent_id') required final int parentId,
      @JsonKey(name: 'missing_slots')
      @_SlotsConverter()
      required final List<int> missingSlots}) = _$IncompleteParentDTOImpl;

  factory _IncompleteParentDTO.fromJson(Map<String, dynamic> json) =
      _$IncompleteParentDTOImpl.fromJson;

  @override
  @JsonKey(name: 'parent_id')
  int get parentId;
  @override
  @JsonKey(name: 'missing_slots')
  @_SlotsConverter()
  List<int> get missingSlots;

  /// Create a copy of IncompleteParentDTO
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$IncompleteParentDTOImplCopyWith<_$IncompleteParentDTOImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
