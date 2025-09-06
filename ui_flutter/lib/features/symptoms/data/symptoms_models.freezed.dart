// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'symptoms_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

IncompleteParent _$IncompleteParentFromJson(Map<String, dynamic> json) {
  return _IncompleteParent.fromJson(json);
}

/// @nodoc
mixin _$IncompleteParent {
  int get parentId => throw _privateConstructorUsedError;
  String get label => throw _privateConstructorUsedError;
  int get depth => throw _privateConstructorUsedError;
  List<int> get missingSlots => throw _privateConstructorUsedError;
  String get path => throw _privateConstructorUsedError;
  DateTime get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this IncompleteParent to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of IncompleteParent
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $IncompleteParentCopyWith<IncompleteParent> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IncompleteParentCopyWith<$Res> {
  factory $IncompleteParentCopyWith(
          IncompleteParent value, $Res Function(IncompleteParent) then) =
      _$IncompleteParentCopyWithImpl<$Res, IncompleteParent>;
  @useResult
  $Res call(
      {int parentId,
      String label,
      int depth,
      List<int> missingSlots,
      String path,
      DateTime updatedAt});
}

/// @nodoc
class _$IncompleteParentCopyWithImpl<$Res, $Val extends IncompleteParent>
    implements $IncompleteParentCopyWith<$Res> {
  _$IncompleteParentCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of IncompleteParent
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? parentId = null,
    Object? label = null,
    Object? depth = null,
    Object? missingSlots = null,
    Object? path = null,
    Object? updatedAt = null,
  }) {
    return _then(_value.copyWith(
      parentId: null == parentId
          ? _value.parentId
          : parentId // ignore: cast_nullable_to_non_nullable
              as int,
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      depth: null == depth
          ? _value.depth
          : depth // ignore: cast_nullable_to_non_nullable
              as int,
      missingSlots: null == missingSlots
          ? _value.missingSlots
          : missingSlots // ignore: cast_nullable_to_non_nullable
              as List<int>,
      path: null == path
          ? _value.path
          : path // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$IncompleteParentImplCopyWith<$Res>
    implements $IncompleteParentCopyWith<$Res> {
  factory _$$IncompleteParentImplCopyWith(_$IncompleteParentImpl value,
          $Res Function(_$IncompleteParentImpl) then) =
      __$$IncompleteParentImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int parentId,
      String label,
      int depth,
      List<int> missingSlots,
      String path,
      DateTime updatedAt});
}

/// @nodoc
class __$$IncompleteParentImplCopyWithImpl<$Res>
    extends _$IncompleteParentCopyWithImpl<$Res, _$IncompleteParentImpl>
    implements _$$IncompleteParentImplCopyWith<$Res> {
  __$$IncompleteParentImplCopyWithImpl(_$IncompleteParentImpl _value,
      $Res Function(_$IncompleteParentImpl) _then)
      : super(_value, _then);

  /// Create a copy of IncompleteParent
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? parentId = null,
    Object? label = null,
    Object? depth = null,
    Object? missingSlots = null,
    Object? path = null,
    Object? updatedAt = null,
  }) {
    return _then(_$IncompleteParentImpl(
      parentId: null == parentId
          ? _value.parentId
          : parentId // ignore: cast_nullable_to_non_nullable
              as int,
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      depth: null == depth
          ? _value.depth
          : depth // ignore: cast_nullable_to_non_nullable
              as int,
      missingSlots: null == missingSlots
          ? _value._missingSlots
          : missingSlots // ignore: cast_nullable_to_non_nullable
              as List<int>,
      path: null == path
          ? _value.path
          : path // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$IncompleteParentImpl implements _IncompleteParent {
  const _$IncompleteParentImpl(
      {required this.parentId,
      required this.label,
      required this.depth,
      required final List<int> missingSlots,
      required this.path,
      required this.updatedAt})
      : _missingSlots = missingSlots;

  factory _$IncompleteParentImpl.fromJson(Map<String, dynamic> json) =>
      _$$IncompleteParentImplFromJson(json);

  @override
  final int parentId;
  @override
  final String label;
  @override
  final int depth;
  final List<int> _missingSlots;
  @override
  List<int> get missingSlots {
    if (_missingSlots is EqualUnmodifiableListView) return _missingSlots;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_missingSlots);
  }

  @override
  final String path;
  @override
  final DateTime updatedAt;

  @override
  String toString() {
    return 'IncompleteParent(parentId: $parentId, label: $label, depth: $depth, missingSlots: $missingSlots, path: $path, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$IncompleteParentImpl &&
            (identical(other.parentId, parentId) ||
                other.parentId == parentId) &&
            (identical(other.label, label) || other.label == label) &&
            (identical(other.depth, depth) || other.depth == depth) &&
            const DeepCollectionEquality()
                .equals(other._missingSlots, _missingSlots) &&
            (identical(other.path, path) || other.path == path) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, parentId, label, depth,
      const DeepCollectionEquality().hash(_missingSlots), path, updatedAt);

  /// Create a copy of IncompleteParent
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$IncompleteParentImplCopyWith<_$IncompleteParentImpl> get copyWith =>
      __$$IncompleteParentImplCopyWithImpl<_$IncompleteParentImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$IncompleteParentImplToJson(
      this,
    );
  }
}

abstract class _IncompleteParent implements IncompleteParent {
  const factory _IncompleteParent(
      {required final int parentId,
      required final String label,
      required final int depth,
      required final List<int> missingSlots,
      required final String path,
      required final DateTime updatedAt}) = _$IncompleteParentImpl;

  factory _IncompleteParent.fromJson(Map<String, dynamic> json) =
      _$IncompleteParentImpl.fromJson;

  @override
  int get parentId;
  @override
  String get label;
  @override
  int get depth;
  @override
  List<int> get missingSlots;
  @override
  String get path;
  @override
  DateTime get updatedAt;

  /// Create a copy of IncompleteParent
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$IncompleteParentImplCopyWith<_$IncompleteParentImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ChildSlot _$ChildSlotFromJson(Map<String, dynamic> json) {
  return _ChildSlot.fromJson(json);
}

/// @nodoc
mixin _$ChildSlot {
  int get slot => throw _privateConstructorUsedError;
  String? get label => throw _privateConstructorUsedError;
  int? get nodeId => throw _privateConstructorUsedError;
  bool? get existing => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;
  String? get warning => throw _privateConstructorUsedError;

  /// Serializes this ChildSlot to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ChildSlot
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ChildSlotCopyWith<ChildSlot> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ChildSlotCopyWith<$Res> {
  factory $ChildSlotCopyWith(ChildSlot value, $Res Function(ChildSlot) then) =
      _$ChildSlotCopyWithImpl<$Res, ChildSlot>;
  @useResult
  $Res call(
      {int slot,
      String? label,
      int? nodeId,
      bool? existing,
      String? error,
      String? warning});
}

/// @nodoc
class _$ChildSlotCopyWithImpl<$Res, $Val extends ChildSlot>
    implements $ChildSlotCopyWith<$Res> {
  _$ChildSlotCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ChildSlot
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? slot = null,
    Object? label = freezed,
    Object? nodeId = freezed,
    Object? existing = freezed,
    Object? error = freezed,
    Object? warning = freezed,
  }) {
    return _then(_value.copyWith(
      slot: null == slot
          ? _value.slot
          : slot // ignore: cast_nullable_to_non_nullable
              as int,
      label: freezed == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String?,
      nodeId: freezed == nodeId
          ? _value.nodeId
          : nodeId // ignore: cast_nullable_to_non_nullable
              as int?,
      existing: freezed == existing
          ? _value.existing
          : existing // ignore: cast_nullable_to_non_nullable
              as bool?,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      warning: freezed == warning
          ? _value.warning
          : warning // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ChildSlotImplCopyWith<$Res>
    implements $ChildSlotCopyWith<$Res> {
  factory _$$ChildSlotImplCopyWith(
          _$ChildSlotImpl value, $Res Function(_$ChildSlotImpl) then) =
      __$$ChildSlotImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int slot,
      String? label,
      int? nodeId,
      bool? existing,
      String? error,
      String? warning});
}

/// @nodoc
class __$$ChildSlotImplCopyWithImpl<$Res>
    extends _$ChildSlotCopyWithImpl<$Res, _$ChildSlotImpl>
    implements _$$ChildSlotImplCopyWith<$Res> {
  __$$ChildSlotImplCopyWithImpl(
      _$ChildSlotImpl _value, $Res Function(_$ChildSlotImpl) _then)
      : super(_value, _then);

  /// Create a copy of ChildSlot
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? slot = null,
    Object? label = freezed,
    Object? nodeId = freezed,
    Object? existing = freezed,
    Object? error = freezed,
    Object? warning = freezed,
  }) {
    return _then(_$ChildSlotImpl(
      slot: null == slot
          ? _value.slot
          : slot // ignore: cast_nullable_to_non_nullable
              as int,
      label: freezed == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String?,
      nodeId: freezed == nodeId
          ? _value.nodeId
          : nodeId // ignore: cast_nullable_to_non_nullable
              as int?,
      existing: freezed == existing
          ? _value.existing
          : existing // ignore: cast_nullable_to_non_nullable
              as bool?,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      warning: freezed == warning
          ? _value.warning
          : warning // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ChildSlotImpl implements _ChildSlot {
  const _$ChildSlotImpl(
      {required this.slot,
      this.label,
      this.nodeId,
      this.existing,
      this.error,
      this.warning});

  factory _$ChildSlotImpl.fromJson(Map<String, dynamic> json) =>
      _$$ChildSlotImplFromJson(json);

  @override
  final int slot;
  @override
  final String? label;
  @override
  final int? nodeId;
  @override
  final bool? existing;
  @override
  final String? error;
  @override
  final String? warning;

  @override
  String toString() {
    return 'ChildSlot(slot: $slot, label: $label, nodeId: $nodeId, existing: $existing, error: $error, warning: $warning)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ChildSlotImpl &&
            (identical(other.slot, slot) || other.slot == slot) &&
            (identical(other.label, label) || other.label == label) &&
            (identical(other.nodeId, nodeId) || other.nodeId == nodeId) &&
            (identical(other.existing, existing) ||
                other.existing == existing) &&
            (identical(other.error, error) || other.error == error) &&
            (identical(other.warning, warning) || other.warning == warning));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, slot, label, nodeId, existing, error, warning);

  /// Create a copy of ChildSlot
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ChildSlotImplCopyWith<_$ChildSlotImpl> get copyWith =>
      __$$ChildSlotImplCopyWithImpl<_$ChildSlotImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ChildSlotImplToJson(
      this,
    );
  }
}

abstract class _ChildSlot implements ChildSlot {
  const factory _ChildSlot(
      {required final int slot,
      final String? label,
      final int? nodeId,
      final bool? existing,
      final String? error,
      final String? warning}) = _$ChildSlotImpl;

  factory _ChildSlot.fromJson(Map<String, dynamic> json) =
      _$ChildSlotImpl.fromJson;

  @override
  int get slot;
  @override
  String? get label;
  @override
  int? get nodeId;
  @override
  bool? get existing;
  @override
  String? get error;
  @override
  String? get warning;

  /// Create a copy of ChildSlot
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ChildSlotImplCopyWith<_$ChildSlotImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ParentChildren _$ParentChildrenFromJson(Map<String, dynamic> json) {
  return _ParentChildren.fromJson(json);
}

/// @nodoc
mixin _$ParentChildren {
  int get parentId => throw _privateConstructorUsedError;
  String get parentLabel => throw _privateConstructorUsedError;
  int get depth => throw _privateConstructorUsedError;
  String get path => throw _privateConstructorUsedError;
  List<ChildSlot> get children => throw _privateConstructorUsedError;
  List<int> get missingSlots => throw _privateConstructorUsedError;
  String? get version => throw _privateConstructorUsedError;
  String? get etag => throw _privateConstructorUsedError;

  /// Serializes this ParentChildren to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ParentChildren
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ParentChildrenCopyWith<ParentChildren> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ParentChildrenCopyWith<$Res> {
  factory $ParentChildrenCopyWith(
          ParentChildren value, $Res Function(ParentChildren) then) =
      _$ParentChildrenCopyWithImpl<$Res, ParentChildren>;
  @useResult
  $Res call(
      {int parentId,
      String parentLabel,
      int depth,
      String path,
      List<ChildSlot> children,
      List<int> missingSlots,
      String? version,
      String? etag});
}

/// @nodoc
class _$ParentChildrenCopyWithImpl<$Res, $Val extends ParentChildren>
    implements $ParentChildrenCopyWith<$Res> {
  _$ParentChildrenCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ParentChildren
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? parentId = null,
    Object? parentLabel = null,
    Object? depth = null,
    Object? path = null,
    Object? children = null,
    Object? missingSlots = null,
    Object? version = freezed,
    Object? etag = freezed,
  }) {
    return _then(_value.copyWith(
      parentId: null == parentId
          ? _value.parentId
          : parentId // ignore: cast_nullable_to_non_nullable
              as int,
      parentLabel: null == parentLabel
          ? _value.parentLabel
          : parentLabel // ignore: cast_nullable_to_non_nullable
              as String,
      depth: null == depth
          ? _value.depth
          : depth // ignore: cast_nullable_to_non_nullable
              as int,
      path: null == path
          ? _value.path
          : path // ignore: cast_nullable_to_non_nullable
              as String,
      children: null == children
          ? _value.children
          : children // ignore: cast_nullable_to_non_nullable
              as List<ChildSlot>,
      missingSlots: null == missingSlots
          ? _value.missingSlots
          : missingSlots // ignore: cast_nullable_to_non_nullable
              as List<int>,
      version: freezed == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as String?,
      etag: freezed == etag
          ? _value.etag
          : etag // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ParentChildrenImplCopyWith<$Res>
    implements $ParentChildrenCopyWith<$Res> {
  factory _$$ParentChildrenImplCopyWith(_$ParentChildrenImpl value,
          $Res Function(_$ParentChildrenImpl) then) =
      __$$ParentChildrenImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int parentId,
      String parentLabel,
      int depth,
      String path,
      List<ChildSlot> children,
      List<int> missingSlots,
      String? version,
      String? etag});
}

/// @nodoc
class __$$ParentChildrenImplCopyWithImpl<$Res>
    extends _$ParentChildrenCopyWithImpl<$Res, _$ParentChildrenImpl>
    implements _$$ParentChildrenImplCopyWith<$Res> {
  __$$ParentChildrenImplCopyWithImpl(
      _$ParentChildrenImpl _value, $Res Function(_$ParentChildrenImpl) _then)
      : super(_value, _then);

  /// Create a copy of ParentChildren
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? parentId = null,
    Object? parentLabel = null,
    Object? depth = null,
    Object? path = null,
    Object? children = null,
    Object? missingSlots = null,
    Object? version = freezed,
    Object? etag = freezed,
  }) {
    return _then(_$ParentChildrenImpl(
      parentId: null == parentId
          ? _value.parentId
          : parentId // ignore: cast_nullable_to_non_nullable
              as int,
      parentLabel: null == parentLabel
          ? _value.parentLabel
          : parentLabel // ignore: cast_nullable_to_non_nullable
              as String,
      depth: null == depth
          ? _value.depth
          : depth // ignore: cast_nullable_to_non_nullable
              as int,
      path: null == path
          ? _value.path
          : path // ignore: cast_nullable_to_non_nullable
              as String,
      children: null == children
          ? _value._children
          : children // ignore: cast_nullable_to_non_nullable
              as List<ChildSlot>,
      missingSlots: null == missingSlots
          ? _value._missingSlots
          : missingSlots // ignore: cast_nullable_to_non_nullable
              as List<int>,
      version: freezed == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as String?,
      etag: freezed == etag
          ? _value.etag
          : etag // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ParentChildrenImpl implements _ParentChildren {
  const _$ParentChildrenImpl(
      {required this.parentId,
      required this.parentLabel,
      required this.depth,
      required this.path,
      required final List<ChildSlot> children,
      required final List<int> missingSlots,
      this.version,
      this.etag})
      : _children = children,
        _missingSlots = missingSlots;

  factory _$ParentChildrenImpl.fromJson(Map<String, dynamic> json) =>
      _$$ParentChildrenImplFromJson(json);

  @override
  final int parentId;
  @override
  final String parentLabel;
  @override
  final int depth;
  @override
  final String path;
  final List<ChildSlot> _children;
  @override
  List<ChildSlot> get children {
    if (_children is EqualUnmodifiableListView) return _children;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_children);
  }

  final List<int> _missingSlots;
  @override
  List<int> get missingSlots {
    if (_missingSlots is EqualUnmodifiableListView) return _missingSlots;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_missingSlots);
  }

  @override
  final String? version;
  @override
  final String? etag;

  @override
  String toString() {
    return 'ParentChildren(parentId: $parentId, parentLabel: $parentLabel, depth: $depth, path: $path, children: $children, missingSlots: $missingSlots, version: $version, etag: $etag)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ParentChildrenImpl &&
            (identical(other.parentId, parentId) ||
                other.parentId == parentId) &&
            (identical(other.parentLabel, parentLabel) ||
                other.parentLabel == parentLabel) &&
            (identical(other.depth, depth) || other.depth == depth) &&
            (identical(other.path, path) || other.path == path) &&
            const DeepCollectionEquality().equals(other._children, _children) &&
            const DeepCollectionEquality()
                .equals(other._missingSlots, _missingSlots) &&
            (identical(other.version, version) || other.version == version) &&
            (identical(other.etag, etag) || other.etag == etag));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      parentId,
      parentLabel,
      depth,
      path,
      const DeepCollectionEquality().hash(_children),
      const DeepCollectionEquality().hash(_missingSlots),
      version,
      etag);

  /// Create a copy of ParentChildren
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ParentChildrenImplCopyWith<_$ParentChildrenImpl> get copyWith =>
      __$$ParentChildrenImplCopyWithImpl<_$ParentChildrenImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ParentChildrenImplToJson(
      this,
    );
  }
}

abstract class _ParentChildren implements ParentChildren {
  const factory _ParentChildren(
      {required final int parentId,
      required final String parentLabel,
      required final int depth,
      required final String path,
      required final List<ChildSlot> children,
      required final List<int> missingSlots,
      final String? version,
      final String? etag}) = _$ParentChildrenImpl;

  factory _ParentChildren.fromJson(Map<String, dynamic> json) =
      _$ParentChildrenImpl.fromJson;

  @override
  int get parentId;
  @override
  String get parentLabel;
  @override
  int get depth;
  @override
  String get path;
  @override
  List<ChildSlot> get children;
  @override
  List<int> get missingSlots;
  @override
  String? get version;
  @override
  String? get etag;

  /// Create a copy of ParentChildren
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ParentChildrenImplCopyWith<_$ParentChildrenImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

BatchAddRequest _$BatchAddRequestFromJson(Map<String, dynamic> json) {
  return _BatchAddRequest.fromJson(json);
}

/// @nodoc
mixin _$BatchAddRequest {
  List<String> get labels => throw _privateConstructorUsedError;
  bool? get replaceExisting => throw _privateConstructorUsedError;

  /// Serializes this BatchAddRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of BatchAddRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $BatchAddRequestCopyWith<BatchAddRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $BatchAddRequestCopyWith<$Res> {
  factory $BatchAddRequestCopyWith(
          BatchAddRequest value, $Res Function(BatchAddRequest) then) =
      _$BatchAddRequestCopyWithImpl<$Res, BatchAddRequest>;
  @useResult
  $Res call({List<String> labels, bool? replaceExisting});
}

/// @nodoc
class _$BatchAddRequestCopyWithImpl<$Res, $Val extends BatchAddRequest>
    implements $BatchAddRequestCopyWith<$Res> {
  _$BatchAddRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of BatchAddRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? labels = null,
    Object? replaceExisting = freezed,
  }) {
    return _then(_value.copyWith(
      labels: null == labels
          ? _value.labels
          : labels // ignore: cast_nullable_to_non_nullable
              as List<String>,
      replaceExisting: freezed == replaceExisting
          ? _value.replaceExisting
          : replaceExisting // ignore: cast_nullable_to_non_nullable
              as bool?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$BatchAddRequestImplCopyWith<$Res>
    implements $BatchAddRequestCopyWith<$Res> {
  factory _$$BatchAddRequestImplCopyWith(_$BatchAddRequestImpl value,
          $Res Function(_$BatchAddRequestImpl) then) =
      __$$BatchAddRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({List<String> labels, bool? replaceExisting});
}

/// @nodoc
class __$$BatchAddRequestImplCopyWithImpl<$Res>
    extends _$BatchAddRequestCopyWithImpl<$Res, _$BatchAddRequestImpl>
    implements _$$BatchAddRequestImplCopyWith<$Res> {
  __$$BatchAddRequestImplCopyWithImpl(
      _$BatchAddRequestImpl _value, $Res Function(_$BatchAddRequestImpl) _then)
      : super(_value, _then);

  /// Create a copy of BatchAddRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? labels = null,
    Object? replaceExisting = freezed,
  }) {
    return _then(_$BatchAddRequestImpl(
      labels: null == labels
          ? _value._labels
          : labels // ignore: cast_nullable_to_non_nullable
              as List<String>,
      replaceExisting: freezed == replaceExisting
          ? _value.replaceExisting
          : replaceExisting // ignore: cast_nullable_to_non_nullable
              as bool?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$BatchAddRequestImpl implements _BatchAddRequest {
  const _$BatchAddRequestImpl(
      {required final List<String> labels, this.replaceExisting})
      : _labels = labels;

  factory _$BatchAddRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$BatchAddRequestImplFromJson(json);

  final List<String> _labels;
  @override
  List<String> get labels {
    if (_labels is EqualUnmodifiableListView) return _labels;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_labels);
  }

  @override
  final bool? replaceExisting;

  @override
  String toString() {
    return 'BatchAddRequest(labels: $labels, replaceExisting: $replaceExisting)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$BatchAddRequestImpl &&
            const DeepCollectionEquality().equals(other._labels, _labels) &&
            (identical(other.replaceExisting, replaceExisting) ||
                other.replaceExisting == replaceExisting));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType,
      const DeepCollectionEquality().hash(_labels), replaceExisting);

  /// Create a copy of BatchAddRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$BatchAddRequestImplCopyWith<_$BatchAddRequestImpl> get copyWith =>
      __$$BatchAddRequestImplCopyWithImpl<_$BatchAddRequestImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$BatchAddRequestImplToJson(
      this,
    );
  }
}

abstract class _BatchAddRequest implements BatchAddRequest {
  const factory _BatchAddRequest(
      {required final List<String> labels,
      final bool? replaceExisting}) = _$BatchAddRequestImpl;

  factory _BatchAddRequest.fromJson(Map<String, dynamic> json) =
      _$BatchAddRequestImpl.fromJson;

  @override
  List<String> get labels;
  @override
  bool? get replaceExisting;

  /// Create a copy of BatchAddRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$BatchAddRequestImplCopyWith<_$BatchAddRequestImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

DictionarySuggestion _$DictionarySuggestionFromJson(Map<String, dynamic> json) {
  return _DictionarySuggestion.fromJson(json);
}

/// @nodoc
mixin _$DictionarySuggestion {
  int get id => throw _privateConstructorUsedError;
  String get term => throw _privateConstructorUsedError;
  String get normalized => throw _privateConstructorUsedError;
  String? get hints => throw _privateConstructorUsedError;
  bool? get isRedFlag => throw _privateConstructorUsedError;

  /// Serializes this DictionarySuggestion to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DictionarySuggestion
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DictionarySuggestionCopyWith<DictionarySuggestion> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DictionarySuggestionCopyWith<$Res> {
  factory $DictionarySuggestionCopyWith(DictionarySuggestion value,
          $Res Function(DictionarySuggestion) then) =
      _$DictionarySuggestionCopyWithImpl<$Res, DictionarySuggestion>;
  @useResult
  $Res call(
      {int id, String term, String normalized, String? hints, bool? isRedFlag});
}

/// @nodoc
class _$DictionarySuggestionCopyWithImpl<$Res,
        $Val extends DictionarySuggestion>
    implements $DictionarySuggestionCopyWith<$Res> {
  _$DictionarySuggestionCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DictionarySuggestion
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? term = null,
    Object? normalized = null,
    Object? hints = freezed,
    Object? isRedFlag = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      term: null == term
          ? _value.term
          : term // ignore: cast_nullable_to_non_nullable
              as String,
      normalized: null == normalized
          ? _value.normalized
          : normalized // ignore: cast_nullable_to_non_nullable
              as String,
      hints: freezed == hints
          ? _value.hints
          : hints // ignore: cast_nullable_to_non_nullable
              as String?,
      isRedFlag: freezed == isRedFlag
          ? _value.isRedFlag
          : isRedFlag // ignore: cast_nullable_to_non_nullable
              as bool?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DictionarySuggestionImplCopyWith<$Res>
    implements $DictionarySuggestionCopyWith<$Res> {
  factory _$$DictionarySuggestionImplCopyWith(_$DictionarySuggestionImpl value,
          $Res Function(_$DictionarySuggestionImpl) then) =
      __$$DictionarySuggestionImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id, String term, String normalized, String? hints, bool? isRedFlag});
}

/// @nodoc
class __$$DictionarySuggestionImplCopyWithImpl<$Res>
    extends _$DictionarySuggestionCopyWithImpl<$Res, _$DictionarySuggestionImpl>
    implements _$$DictionarySuggestionImplCopyWith<$Res> {
  __$$DictionarySuggestionImplCopyWithImpl(_$DictionarySuggestionImpl _value,
      $Res Function(_$DictionarySuggestionImpl) _then)
      : super(_value, _then);

  /// Create a copy of DictionarySuggestion
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? term = null,
    Object? normalized = null,
    Object? hints = freezed,
    Object? isRedFlag = freezed,
  }) {
    return _then(_$DictionarySuggestionImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      term: null == term
          ? _value.term
          : term // ignore: cast_nullable_to_non_nullable
              as String,
      normalized: null == normalized
          ? _value.normalized
          : normalized // ignore: cast_nullable_to_non_nullable
              as String,
      hints: freezed == hints
          ? _value.hints
          : hints // ignore: cast_nullable_to_non_nullable
              as String?,
      isRedFlag: freezed == isRedFlag
          ? _value.isRedFlag
          : isRedFlag // ignore: cast_nullable_to_non_nullable
              as bool?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DictionarySuggestionImpl implements _DictionarySuggestion {
  const _$DictionarySuggestionImpl(
      {required this.id,
      required this.term,
      required this.normalized,
      this.hints,
      this.isRedFlag});

  factory _$DictionarySuggestionImpl.fromJson(Map<String, dynamic> json) =>
      _$$DictionarySuggestionImplFromJson(json);

  @override
  final int id;
  @override
  final String term;
  @override
  final String normalized;
  @override
  final String? hints;
  @override
  final bool? isRedFlag;

  @override
  String toString() {
    return 'DictionarySuggestion(id: $id, term: $term, normalized: $normalized, hints: $hints, isRedFlag: $isRedFlag)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DictionarySuggestionImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.term, term) || other.term == term) &&
            (identical(other.normalized, normalized) ||
                other.normalized == normalized) &&
            (identical(other.hints, hints) || other.hints == hints) &&
            (identical(other.isRedFlag, isRedFlag) ||
                other.isRedFlag == isRedFlag));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, id, term, normalized, hints, isRedFlag);

  /// Create a copy of DictionarySuggestion
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DictionarySuggestionImplCopyWith<_$DictionarySuggestionImpl>
      get copyWith =>
          __$$DictionarySuggestionImplCopyWithImpl<_$DictionarySuggestionImpl>(
              this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DictionarySuggestionImplToJson(
      this,
    );
  }
}

abstract class _DictionarySuggestion implements DictionarySuggestion {
  const factory _DictionarySuggestion(
      {required final int id,
      required final String term,
      required final String normalized,
      final String? hints,
      final bool? isRedFlag}) = _$DictionarySuggestionImpl;

  factory _DictionarySuggestion.fromJson(Map<String, dynamic> json) =
      _$DictionarySuggestionImpl.fromJson;

  @override
  int get id;
  @override
  String get term;
  @override
  String get normalized;
  @override
  String? get hints;
  @override
  bool? get isRedFlag;

  /// Create a copy of DictionarySuggestion
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DictionarySuggestionImplCopyWith<_$DictionarySuggestionImpl>
      get copyWith => throw _privateConstructorUsedError;
}

ParentStatus _$ParentStatusFromJson(Map<String, dynamic> json) {
  return _ParentStatus.fromJson(json);
}

/// @nodoc
mixin _$ParentStatus {
  String get status => throw _privateConstructorUsedError;
  String? get message => throw _privateConstructorUsedError;
  int? get filledCount => throw _privateConstructorUsedError;
  int? get totalCount => throw _privateConstructorUsedError;

  /// Serializes this ParentStatus to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ParentStatus
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ParentStatusCopyWith<ParentStatus> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ParentStatusCopyWith<$Res> {
  factory $ParentStatusCopyWith(
          ParentStatus value, $Res Function(ParentStatus) then) =
      _$ParentStatusCopyWithImpl<$Res, ParentStatus>;
  @useResult
  $Res call(
      {String status, String? message, int? filledCount, int? totalCount});
}

/// @nodoc
class _$ParentStatusCopyWithImpl<$Res, $Val extends ParentStatus>
    implements $ParentStatusCopyWith<$Res> {
  _$ParentStatusCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ParentStatus
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? status = null,
    Object? message = freezed,
    Object? filledCount = freezed,
    Object? totalCount = freezed,
  }) {
    return _then(_value.copyWith(
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      message: freezed == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String?,
      filledCount: freezed == filledCount
          ? _value.filledCount
          : filledCount // ignore: cast_nullable_to_non_nullable
              as int?,
      totalCount: freezed == totalCount
          ? _value.totalCount
          : totalCount // ignore: cast_nullable_to_non_nullable
              as int?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ParentStatusImplCopyWith<$Res>
    implements $ParentStatusCopyWith<$Res> {
  factory _$$ParentStatusImplCopyWith(
          _$ParentStatusImpl value, $Res Function(_$ParentStatusImpl) then) =
      __$$ParentStatusImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String status, String? message, int? filledCount, int? totalCount});
}

/// @nodoc
class __$$ParentStatusImplCopyWithImpl<$Res>
    extends _$ParentStatusCopyWithImpl<$Res, _$ParentStatusImpl>
    implements _$$ParentStatusImplCopyWith<$Res> {
  __$$ParentStatusImplCopyWithImpl(
      _$ParentStatusImpl _value, $Res Function(_$ParentStatusImpl) _then)
      : super(_value, _then);

  /// Create a copy of ParentStatus
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? status = null,
    Object? message = freezed,
    Object? filledCount = freezed,
    Object? totalCount = freezed,
  }) {
    return _then(_$ParentStatusImpl(
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      message: freezed == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String?,
      filledCount: freezed == filledCount
          ? _value.filledCount
          : filledCount // ignore: cast_nullable_to_non_nullable
              as int?,
      totalCount: freezed == totalCount
          ? _value.totalCount
          : totalCount // ignore: cast_nullable_to_non_nullable
              as int?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ParentStatusImpl implements _ParentStatus {
  const _$ParentStatusImpl(
      {required this.status, this.message, this.filledCount, this.totalCount});

  factory _$ParentStatusImpl.fromJson(Map<String, dynamic> json) =>
      _$$ParentStatusImplFromJson(json);

  @override
  final String status;
  @override
  final String? message;
  @override
  final int? filledCount;
  @override
  final int? totalCount;

  @override
  String toString() {
    return 'ParentStatus(status: $status, message: $message, filledCount: $filledCount, totalCount: $totalCount)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ParentStatusImpl &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.message, message) || other.message == message) &&
            (identical(other.filledCount, filledCount) ||
                other.filledCount == filledCount) &&
            (identical(other.totalCount, totalCount) ||
                other.totalCount == totalCount));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, status, message, filledCount, totalCount);

  /// Create a copy of ParentStatus
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ParentStatusImplCopyWith<_$ParentStatusImpl> get copyWith =>
      __$$ParentStatusImplCopyWithImpl<_$ParentStatusImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ParentStatusImplToJson(
      this,
    );
  }
}

abstract class _ParentStatus implements ParentStatus {
  const factory _ParentStatus(
      {required final String status,
      final String? message,
      final int? filledCount,
      final int? totalCount}) = _$ParentStatusImpl;

  factory _ParentStatus.fromJson(Map<String, dynamic> json) =
      _$ParentStatusImpl.fromJson;

  @override
  String get status;
  @override
  String? get message;
  @override
  int? get filledCount;
  @override
  int? get totalCount;

  /// Create a copy of ParentStatus
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ParentStatusImplCopyWith<_$ParentStatusImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ChildrenUpdateIn _$ChildrenUpdateInFromJson(Map<String, dynamic> json) {
  return _ChildrenUpdateIn.fromJson(json);
}

/// @nodoc
mixin _$ChildrenUpdateIn {
  String? get version => throw _privateConstructorUsedError;
  List<ChildSlot> get children => throw _privateConstructorUsedError;

  /// Serializes this ChildrenUpdateIn to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ChildrenUpdateIn
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ChildrenUpdateInCopyWith<ChildrenUpdateIn> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ChildrenUpdateInCopyWith<$Res> {
  factory $ChildrenUpdateInCopyWith(
          ChildrenUpdateIn value, $Res Function(ChildrenUpdateIn) then) =
      _$ChildrenUpdateInCopyWithImpl<$Res, ChildrenUpdateIn>;
  @useResult
  $Res call({String? version, List<ChildSlot> children});
}

/// @nodoc
class _$ChildrenUpdateInCopyWithImpl<$Res, $Val extends ChildrenUpdateIn>
    implements $ChildrenUpdateInCopyWith<$Res> {
  _$ChildrenUpdateInCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ChildrenUpdateIn
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? version = freezed,
    Object? children = null,
  }) {
    return _then(_value.copyWith(
      version: freezed == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as String?,
      children: null == children
          ? _value.children
          : children // ignore: cast_nullable_to_non_nullable
              as List<ChildSlot>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ChildrenUpdateInImplCopyWith<$Res>
    implements $ChildrenUpdateInCopyWith<$Res> {
  factory _$$ChildrenUpdateInImplCopyWith(_$ChildrenUpdateInImpl value,
          $Res Function(_$ChildrenUpdateInImpl) then) =
      __$$ChildrenUpdateInImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String? version, List<ChildSlot> children});
}

/// @nodoc
class __$$ChildrenUpdateInImplCopyWithImpl<$Res>
    extends _$ChildrenUpdateInCopyWithImpl<$Res, _$ChildrenUpdateInImpl>
    implements _$$ChildrenUpdateInImplCopyWith<$Res> {
  __$$ChildrenUpdateInImplCopyWithImpl(_$ChildrenUpdateInImpl _value,
      $Res Function(_$ChildrenUpdateInImpl) _then)
      : super(_value, _then);

  /// Create a copy of ChildrenUpdateIn
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? version = freezed,
    Object? children = null,
  }) {
    return _then(_$ChildrenUpdateInImpl(
      version: freezed == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as String?,
      children: null == children
          ? _value._children
          : children // ignore: cast_nullable_to_non_nullable
              as List<ChildSlot>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ChildrenUpdateInImpl implements _ChildrenUpdateIn {
  const _$ChildrenUpdateInImpl(
      {this.version, required final List<ChildSlot> children})
      : _children = children;

  factory _$ChildrenUpdateInImpl.fromJson(Map<String, dynamic> json) =>
      _$$ChildrenUpdateInImplFromJson(json);

  @override
  final String? version;
  final List<ChildSlot> _children;
  @override
  List<ChildSlot> get children {
    if (_children is EqualUnmodifiableListView) return _children;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_children);
  }

  @override
  String toString() {
    return 'ChildrenUpdateIn(version: $version, children: $children)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ChildrenUpdateInImpl &&
            (identical(other.version, version) || other.version == version) &&
            const DeepCollectionEquality().equals(other._children, _children));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, version, const DeepCollectionEquality().hash(_children));

  /// Create a copy of ChildrenUpdateIn
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ChildrenUpdateInImplCopyWith<_$ChildrenUpdateInImpl> get copyWith =>
      __$$ChildrenUpdateInImplCopyWithImpl<_$ChildrenUpdateInImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ChildrenUpdateInImplToJson(
      this,
    );
  }
}

abstract class _ChildrenUpdateIn implements ChildrenUpdateIn {
  const factory _ChildrenUpdateIn(
      {final String? version,
      required final List<ChildSlot> children}) = _$ChildrenUpdateInImpl;

  factory _ChildrenUpdateIn.fromJson(Map<String, dynamic> json) =
      _$ChildrenUpdateInImpl.fromJson;

  @override
  String? get version;
  @override
  List<ChildSlot> get children;

  /// Create a copy of ChildrenUpdateIn
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ChildrenUpdateInImplCopyWith<_$ChildrenUpdateInImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ChildrenUpdateOut _$ChildrenUpdateOutFromJson(Map<String, dynamic> json) {
  return _ChildrenUpdateOut.fromJson(json);
}

/// @nodoc
mixin _$ChildrenUpdateOut {
  int get parentId => throw _privateConstructorUsedError;
  int get version => throw _privateConstructorUsedError;
  List<int> get missingSlots => throw _privateConstructorUsedError;
  List<int> get updated => throw _privateConstructorUsedError;

  /// Serializes this ChildrenUpdateOut to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ChildrenUpdateOut
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ChildrenUpdateOutCopyWith<ChildrenUpdateOut> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ChildrenUpdateOutCopyWith<$Res> {
  factory $ChildrenUpdateOutCopyWith(
          ChildrenUpdateOut value, $Res Function(ChildrenUpdateOut) then) =
      _$ChildrenUpdateOutCopyWithImpl<$Res, ChildrenUpdateOut>;
  @useResult
  $Res call(
      {int parentId, int version, List<int> missingSlots, List<int> updated});
}

/// @nodoc
class _$ChildrenUpdateOutCopyWithImpl<$Res, $Val extends ChildrenUpdateOut>
    implements $ChildrenUpdateOutCopyWith<$Res> {
  _$ChildrenUpdateOutCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ChildrenUpdateOut
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? parentId = null,
    Object? version = null,
    Object? missingSlots = null,
    Object? updated = null,
  }) {
    return _then(_value.copyWith(
      parentId: null == parentId
          ? _value.parentId
          : parentId // ignore: cast_nullable_to_non_nullable
              as int,
      version: null == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as int,
      missingSlots: null == missingSlots
          ? _value.missingSlots
          : missingSlots // ignore: cast_nullable_to_non_nullable
              as List<int>,
      updated: null == updated
          ? _value.updated
          : updated // ignore: cast_nullable_to_non_nullable
              as List<int>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ChildrenUpdateOutImplCopyWith<$Res>
    implements $ChildrenUpdateOutCopyWith<$Res> {
  factory _$$ChildrenUpdateOutImplCopyWith(_$ChildrenUpdateOutImpl value,
          $Res Function(_$ChildrenUpdateOutImpl) then) =
      __$$ChildrenUpdateOutImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int parentId, int version, List<int> missingSlots, List<int> updated});
}

/// @nodoc
class __$$ChildrenUpdateOutImplCopyWithImpl<$Res>
    extends _$ChildrenUpdateOutCopyWithImpl<$Res, _$ChildrenUpdateOutImpl>
    implements _$$ChildrenUpdateOutImplCopyWith<$Res> {
  __$$ChildrenUpdateOutImplCopyWithImpl(_$ChildrenUpdateOutImpl _value,
      $Res Function(_$ChildrenUpdateOutImpl) _then)
      : super(_value, _then);

  /// Create a copy of ChildrenUpdateOut
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? parentId = null,
    Object? version = null,
    Object? missingSlots = null,
    Object? updated = null,
  }) {
    return _then(_$ChildrenUpdateOutImpl(
      parentId: null == parentId
          ? _value.parentId
          : parentId // ignore: cast_nullable_to_non_nullable
              as int,
      version: null == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as int,
      missingSlots: null == missingSlots
          ? _value._missingSlots
          : missingSlots // ignore: cast_nullable_to_non_nullable
              as List<int>,
      updated: null == updated
          ? _value._updated
          : updated // ignore: cast_nullable_to_non_nullable
              as List<int>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ChildrenUpdateOutImpl implements _ChildrenUpdateOut {
  const _$ChildrenUpdateOutImpl(
      {required this.parentId,
      required this.version,
      required final List<int> missingSlots,
      required final List<int> updated})
      : _missingSlots = missingSlots,
        _updated = updated;

  factory _$ChildrenUpdateOutImpl.fromJson(Map<String, dynamic> json) =>
      _$$ChildrenUpdateOutImplFromJson(json);

  @override
  final int parentId;
  @override
  final int version;
  final List<int> _missingSlots;
  @override
  List<int> get missingSlots {
    if (_missingSlots is EqualUnmodifiableListView) return _missingSlots;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_missingSlots);
  }

  final List<int> _updated;
  @override
  List<int> get updated {
    if (_updated is EqualUnmodifiableListView) return _updated;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_updated);
  }

  @override
  String toString() {
    return 'ChildrenUpdateOut(parentId: $parentId, version: $version, missingSlots: $missingSlots, updated: $updated)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ChildrenUpdateOutImpl &&
            (identical(other.parentId, parentId) ||
                other.parentId == parentId) &&
            (identical(other.version, version) || other.version == version) &&
            const DeepCollectionEquality()
                .equals(other._missingSlots, _missingSlots) &&
            const DeepCollectionEquality().equals(other._updated, _updated));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      parentId,
      version,
      const DeepCollectionEquality().hash(_missingSlots),
      const DeepCollectionEquality().hash(_updated));

  /// Create a copy of ChildrenUpdateOut
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ChildrenUpdateOutImplCopyWith<_$ChildrenUpdateOutImpl> get copyWith =>
      __$$ChildrenUpdateOutImplCopyWithImpl<_$ChildrenUpdateOutImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ChildrenUpdateOutImplToJson(
      this,
    );
  }
}

abstract class _ChildrenUpdateOut implements ChildrenUpdateOut {
  const factory _ChildrenUpdateOut(
      {required final int parentId,
      required final int version,
      required final List<int> missingSlots,
      required final List<int> updated}) = _$ChildrenUpdateOutImpl;

  factory _ChildrenUpdateOut.fromJson(Map<String, dynamic> json) =
      _$ChildrenUpdateOutImpl.fromJson;

  @override
  int get parentId;
  @override
  int get version;
  @override
  List<int> get missingSlots;
  @override
  List<int> get updated;

  /// Create a copy of ChildrenUpdateOut
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ChildrenUpdateOutImplCopyWith<_$ChildrenUpdateOutImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

MaterializationResult _$MaterializationResultFromJson(
    Map<String, dynamic> json) {
  return _MaterializationResult.fromJson(json);
}

/// @nodoc
mixin _$MaterializationResult {
  int get added => throw _privateConstructorUsedError;
  int get filled => throw _privateConstructorUsedError;
  int get pruned => throw _privateConstructorUsedError;
  int get kept => throw _privateConstructorUsedError;
  String? get log => throw _privateConstructorUsedError;
  DateTime? get timestamp => throw _privateConstructorUsedError;
  List<String>? get details => throw _privateConstructorUsedError;

  /// Serializes this MaterializationResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of MaterializationResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $MaterializationResultCopyWith<MaterializationResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $MaterializationResultCopyWith<$Res> {
  factory $MaterializationResultCopyWith(MaterializationResult value,
          $Res Function(MaterializationResult) then) =
      _$MaterializationResultCopyWithImpl<$Res, MaterializationResult>;
  @useResult
  $Res call(
      {int added,
      int filled,
      int pruned,
      int kept,
      String? log,
      DateTime? timestamp,
      List<String>? details});
}

/// @nodoc
class _$MaterializationResultCopyWithImpl<$Res,
        $Val extends MaterializationResult>
    implements $MaterializationResultCopyWith<$Res> {
  _$MaterializationResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of MaterializationResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? added = null,
    Object? filled = null,
    Object? pruned = null,
    Object? kept = null,
    Object? log = freezed,
    Object? timestamp = freezed,
    Object? details = freezed,
  }) {
    return _then(_value.copyWith(
      added: null == added
          ? _value.added
          : added // ignore: cast_nullable_to_non_nullable
              as int,
      filled: null == filled
          ? _value.filled
          : filled // ignore: cast_nullable_to_non_nullable
              as int,
      pruned: null == pruned
          ? _value.pruned
          : pruned // ignore: cast_nullable_to_non_nullable
              as int,
      kept: null == kept
          ? _value.kept
          : kept // ignore: cast_nullable_to_non_nullable
              as int,
      log: freezed == log
          ? _value.log
          : log // ignore: cast_nullable_to_non_nullable
              as String?,
      timestamp: freezed == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      details: freezed == details
          ? _value.details
          : details // ignore: cast_nullable_to_non_nullable
              as List<String>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$MaterializationResultImplCopyWith<$Res>
    implements $MaterializationResultCopyWith<$Res> {
  factory _$$MaterializationResultImplCopyWith(
          _$MaterializationResultImpl value,
          $Res Function(_$MaterializationResultImpl) then) =
      __$$MaterializationResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int added,
      int filled,
      int pruned,
      int kept,
      String? log,
      DateTime? timestamp,
      List<String>? details});
}

/// @nodoc
class __$$MaterializationResultImplCopyWithImpl<$Res>
    extends _$MaterializationResultCopyWithImpl<$Res,
        _$MaterializationResultImpl>
    implements _$$MaterializationResultImplCopyWith<$Res> {
  __$$MaterializationResultImplCopyWithImpl(_$MaterializationResultImpl _value,
      $Res Function(_$MaterializationResultImpl) _then)
      : super(_value, _then);

  /// Create a copy of MaterializationResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? added = null,
    Object? filled = null,
    Object? pruned = null,
    Object? kept = null,
    Object? log = freezed,
    Object? timestamp = freezed,
    Object? details = freezed,
  }) {
    return _then(_$MaterializationResultImpl(
      added: null == added
          ? _value.added
          : added // ignore: cast_nullable_to_non_nullable
              as int,
      filled: null == filled
          ? _value.filled
          : filled // ignore: cast_nullable_to_non_nullable
              as int,
      pruned: null == pruned
          ? _value.pruned
          : pruned // ignore: cast_nullable_to_non_nullable
              as int,
      kept: null == kept
          ? _value.kept
          : kept // ignore: cast_nullable_to_non_nullable
              as int,
      log: freezed == log
          ? _value.log
          : log // ignore: cast_nullable_to_non_nullable
              as String?,
      timestamp: freezed == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      details: freezed == details
          ? _value._details
          : details // ignore: cast_nullable_to_non_nullable
              as List<String>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$MaterializationResultImpl implements _MaterializationResult {
  const _$MaterializationResultImpl(
      {required this.added,
      required this.filled,
      required this.pruned,
      required this.kept,
      this.log,
      this.timestamp,
      final List<String>? details})
      : _details = details;

  factory _$MaterializationResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$MaterializationResultImplFromJson(json);

  @override
  final int added;
  @override
  final int filled;
  @override
  final int pruned;
  @override
  final int kept;
  @override
  final String? log;
  @override
  final DateTime? timestamp;
  final List<String>? _details;
  @override
  List<String>? get details {
    final value = _details;
    if (value == null) return null;
    if (_details is EqualUnmodifiableListView) return _details;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  @override
  String toString() {
    return 'MaterializationResult(added: $added, filled: $filled, pruned: $pruned, kept: $kept, log: $log, timestamp: $timestamp, details: $details)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$MaterializationResultImpl &&
            (identical(other.added, added) || other.added == added) &&
            (identical(other.filled, filled) || other.filled == filled) &&
            (identical(other.pruned, pruned) || other.pruned == pruned) &&
            (identical(other.kept, kept) || other.kept == kept) &&
            (identical(other.log, log) || other.log == log) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            const DeepCollectionEquality().equals(other._details, _details));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, added, filled, pruned, kept, log,
      timestamp, const DeepCollectionEquality().hash(_details));

  /// Create a copy of MaterializationResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$MaterializationResultImplCopyWith<_$MaterializationResultImpl>
      get copyWith => __$$MaterializationResultImplCopyWithImpl<
          _$MaterializationResultImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$MaterializationResultImplToJson(
      this,
    );
  }
}

abstract class _MaterializationResult implements MaterializationResult {
  const factory _MaterializationResult(
      {required final int added,
      required final int filled,
      required final int pruned,
      required final int kept,
      final String? log,
      final DateTime? timestamp,
      final List<String>? details}) = _$MaterializationResultImpl;

  factory _MaterializationResult.fromJson(Map<String, dynamic> json) =
      _$MaterializationResultImpl.fromJson;

  @override
  int get added;
  @override
  int get filled;
  @override
  int get pruned;
  @override
  int get kept;
  @override
  String? get log;
  @override
  DateTime? get timestamp;
  @override
  List<String>? get details;

  /// Create a copy of MaterializationResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$MaterializationResultImplCopyWith<_$MaterializationResultImpl>
      get copyWith => throw _privateConstructorUsedError;
}

MaterializationHistoryItem _$MaterializationHistoryItemFromJson(
    Map<String, dynamic> json) {
  return _MaterializationHistoryItem.fromJson(json);
}

/// @nodoc
mixin _$MaterializationHistoryItem {
  int get id => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError;
  String get operation => throw _privateConstructorUsedError;
  MaterializationResult get result => throw _privateConstructorUsedError;
  List<int>? get parentIds => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;

  /// Serializes this MaterializationHistoryItem to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of MaterializationHistoryItem
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $MaterializationHistoryItemCopyWith<MaterializationHistoryItem>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $MaterializationHistoryItemCopyWith<$Res> {
  factory $MaterializationHistoryItemCopyWith(MaterializationHistoryItem value,
          $Res Function(MaterializationHistoryItem) then) =
      _$MaterializationHistoryItemCopyWithImpl<$Res,
          MaterializationHistoryItem>;
  @useResult
  $Res call(
      {int id,
      DateTime timestamp,
      String operation,
      MaterializationResult result,
      List<int>? parentIds,
      String? description});

  $MaterializationResultCopyWith<$Res> get result;
}

/// @nodoc
class _$MaterializationHistoryItemCopyWithImpl<$Res,
        $Val extends MaterializationHistoryItem>
    implements $MaterializationHistoryItemCopyWith<$Res> {
  _$MaterializationHistoryItemCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of MaterializationHistoryItem
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? timestamp = null,
    Object? operation = null,
    Object? result = null,
    Object? parentIds = freezed,
    Object? description = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      operation: null == operation
          ? _value.operation
          : operation // ignore: cast_nullable_to_non_nullable
              as String,
      result: null == result
          ? _value.result
          : result // ignore: cast_nullable_to_non_nullable
              as MaterializationResult,
      parentIds: freezed == parentIds
          ? _value.parentIds
          : parentIds // ignore: cast_nullable_to_non_nullable
              as List<int>?,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }

  /// Create a copy of MaterializationHistoryItem
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $MaterializationResultCopyWith<$Res> get result {
    return $MaterializationResultCopyWith<$Res>(_value.result, (value) {
      return _then(_value.copyWith(result: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$MaterializationHistoryItemImplCopyWith<$Res>
    implements $MaterializationHistoryItemCopyWith<$Res> {
  factory _$$MaterializationHistoryItemImplCopyWith(
          _$MaterializationHistoryItemImpl value,
          $Res Function(_$MaterializationHistoryItemImpl) then) =
      __$$MaterializationHistoryItemImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id,
      DateTime timestamp,
      String operation,
      MaterializationResult result,
      List<int>? parentIds,
      String? description});

  @override
  $MaterializationResultCopyWith<$Res> get result;
}

/// @nodoc
class __$$MaterializationHistoryItemImplCopyWithImpl<$Res>
    extends _$MaterializationHistoryItemCopyWithImpl<$Res,
        _$MaterializationHistoryItemImpl>
    implements _$$MaterializationHistoryItemImplCopyWith<$Res> {
  __$$MaterializationHistoryItemImplCopyWithImpl(
      _$MaterializationHistoryItemImpl _value,
      $Res Function(_$MaterializationHistoryItemImpl) _then)
      : super(_value, _then);

  /// Create a copy of MaterializationHistoryItem
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? timestamp = null,
    Object? operation = null,
    Object? result = null,
    Object? parentIds = freezed,
    Object? description = freezed,
  }) {
    return _then(_$MaterializationHistoryItemImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      operation: null == operation
          ? _value.operation
          : operation // ignore: cast_nullable_to_non_nullable
              as String,
      result: null == result
          ? _value.result
          : result // ignore: cast_nullable_to_non_nullable
              as MaterializationResult,
      parentIds: freezed == parentIds
          ? _value._parentIds
          : parentIds // ignore: cast_nullable_to_non_nullable
              as List<int>?,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$MaterializationHistoryItemImpl implements _MaterializationHistoryItem {
  const _$MaterializationHistoryItemImpl(
      {required this.id,
      required this.timestamp,
      required this.operation,
      required this.result,
      final List<int>? parentIds,
      this.description})
      : _parentIds = parentIds;

  factory _$MaterializationHistoryItemImpl.fromJson(
          Map<String, dynamic> json) =>
      _$$MaterializationHistoryItemImplFromJson(json);

  @override
  final int id;
  @override
  final DateTime timestamp;
  @override
  final String operation;
  @override
  final MaterializationResult result;
  final List<int>? _parentIds;
  @override
  List<int>? get parentIds {
    final value = _parentIds;
    if (value == null) return null;
    if (_parentIds is EqualUnmodifiableListView) return _parentIds;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  @override
  final String? description;

  @override
  String toString() {
    return 'MaterializationHistoryItem(id: $id, timestamp: $timestamp, operation: $operation, result: $result, parentIds: $parentIds, description: $description)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$MaterializationHistoryItemImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            (identical(other.operation, operation) ||
                other.operation == operation) &&
            (identical(other.result, result) || other.result == result) &&
            const DeepCollectionEquality()
                .equals(other._parentIds, _parentIds) &&
            (identical(other.description, description) ||
                other.description == description));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, timestamp, operation, result,
      const DeepCollectionEquality().hash(_parentIds), description);

  /// Create a copy of MaterializationHistoryItem
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$MaterializationHistoryItemImplCopyWith<_$MaterializationHistoryItemImpl>
      get copyWith => __$$MaterializationHistoryItemImplCopyWithImpl<
          _$MaterializationHistoryItemImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$MaterializationHistoryItemImplToJson(
      this,
    );
  }
}

abstract class _MaterializationHistoryItem
    implements MaterializationHistoryItem {
  const factory _MaterializationHistoryItem(
      {required final int id,
      required final DateTime timestamp,
      required final String operation,
      required final MaterializationResult result,
      final List<int>? parentIds,
      final String? description}) = _$MaterializationHistoryItemImpl;

  factory _MaterializationHistoryItem.fromJson(Map<String, dynamic> json) =
      _$MaterializationHistoryItemImpl.fromJson;

  @override
  int get id;
  @override
  DateTime get timestamp;
  @override
  String get operation;
  @override
  MaterializationResult get result;
  @override
  List<int>? get parentIds;
  @override
  String? get description;

  /// Create a copy of MaterializationHistoryItem
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$MaterializationHistoryItemImplCopyWith<_$MaterializationHistoryItemImpl>
      get copyWith => throw _privateConstructorUsedError;
}

MaterializationPreview _$MaterializationPreviewFromJson(
    Map<String, dynamic> json) {
  return _MaterializationPreview.fromJson(json);
}

/// @nodoc
mixin _$MaterializationPreview {
  int get parentId => throw _privateConstructorUsedError;
  List<String> get willAdd => throw _privateConstructorUsedError;
  List<String> get willFill => throw _privateConstructorUsedError;
  List<String> get willPrune => throw _privateConstructorUsedError;
  List<String> get willKeep => throw _privateConstructorUsedError;
  String? get warnings => throw _privateConstructorUsedError;
  bool? get canUndo => throw _privateConstructorUsedError;

  /// Serializes this MaterializationPreview to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of MaterializationPreview
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $MaterializationPreviewCopyWith<MaterializationPreview> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $MaterializationPreviewCopyWith<$Res> {
  factory $MaterializationPreviewCopyWith(MaterializationPreview value,
          $Res Function(MaterializationPreview) then) =
      _$MaterializationPreviewCopyWithImpl<$Res, MaterializationPreview>;
  @useResult
  $Res call(
      {int parentId,
      List<String> willAdd,
      List<String> willFill,
      List<String> willPrune,
      List<String> willKeep,
      String? warnings,
      bool? canUndo});
}

/// @nodoc
class _$MaterializationPreviewCopyWithImpl<$Res,
        $Val extends MaterializationPreview>
    implements $MaterializationPreviewCopyWith<$Res> {
  _$MaterializationPreviewCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of MaterializationPreview
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? parentId = null,
    Object? willAdd = null,
    Object? willFill = null,
    Object? willPrune = null,
    Object? willKeep = null,
    Object? warnings = freezed,
    Object? canUndo = freezed,
  }) {
    return _then(_value.copyWith(
      parentId: null == parentId
          ? _value.parentId
          : parentId // ignore: cast_nullable_to_non_nullable
              as int,
      willAdd: null == willAdd
          ? _value.willAdd
          : willAdd // ignore: cast_nullable_to_non_nullable
              as List<String>,
      willFill: null == willFill
          ? _value.willFill
          : willFill // ignore: cast_nullable_to_non_nullable
              as List<String>,
      willPrune: null == willPrune
          ? _value.willPrune
          : willPrune // ignore: cast_nullable_to_non_nullable
              as List<String>,
      willKeep: null == willKeep
          ? _value.willKeep
          : willKeep // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warnings: freezed == warnings
          ? _value.warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as String?,
      canUndo: freezed == canUndo
          ? _value.canUndo
          : canUndo // ignore: cast_nullable_to_non_nullable
              as bool?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$MaterializationPreviewImplCopyWith<$Res>
    implements $MaterializationPreviewCopyWith<$Res> {
  factory _$$MaterializationPreviewImplCopyWith(
          _$MaterializationPreviewImpl value,
          $Res Function(_$MaterializationPreviewImpl) then) =
      __$$MaterializationPreviewImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int parentId,
      List<String> willAdd,
      List<String> willFill,
      List<String> willPrune,
      List<String> willKeep,
      String? warnings,
      bool? canUndo});
}

/// @nodoc
class __$$MaterializationPreviewImplCopyWithImpl<$Res>
    extends _$MaterializationPreviewCopyWithImpl<$Res,
        _$MaterializationPreviewImpl>
    implements _$$MaterializationPreviewImplCopyWith<$Res> {
  __$$MaterializationPreviewImplCopyWithImpl(
      _$MaterializationPreviewImpl _value,
      $Res Function(_$MaterializationPreviewImpl) _then)
      : super(_value, _then);

  /// Create a copy of MaterializationPreview
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? parentId = null,
    Object? willAdd = null,
    Object? willFill = null,
    Object? willPrune = null,
    Object? willKeep = null,
    Object? warnings = freezed,
    Object? canUndo = freezed,
  }) {
    return _then(_$MaterializationPreviewImpl(
      parentId: null == parentId
          ? _value.parentId
          : parentId // ignore: cast_nullable_to_non_nullable
              as int,
      willAdd: null == willAdd
          ? _value._willAdd
          : willAdd // ignore: cast_nullable_to_non_nullable
              as List<String>,
      willFill: null == willFill
          ? _value._willFill
          : willFill // ignore: cast_nullable_to_non_nullable
              as List<String>,
      willPrune: null == willPrune
          ? _value._willPrune
          : willPrune // ignore: cast_nullable_to_non_nullable
              as List<String>,
      willKeep: null == willKeep
          ? _value._willKeep
          : willKeep // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warnings: freezed == warnings
          ? _value.warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as String?,
      canUndo: freezed == canUndo
          ? _value.canUndo
          : canUndo // ignore: cast_nullable_to_non_nullable
              as bool?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$MaterializationPreviewImpl implements _MaterializationPreview {
  const _$MaterializationPreviewImpl(
      {required this.parentId,
      required final List<String> willAdd,
      required final List<String> willFill,
      required final List<String> willPrune,
      required final List<String> willKeep,
      this.warnings,
      this.canUndo})
      : _willAdd = willAdd,
        _willFill = willFill,
        _willPrune = willPrune,
        _willKeep = willKeep;

  factory _$MaterializationPreviewImpl.fromJson(Map<String, dynamic> json) =>
      _$$MaterializationPreviewImplFromJson(json);

  @override
  final int parentId;
  final List<String> _willAdd;
  @override
  List<String> get willAdd {
    if (_willAdd is EqualUnmodifiableListView) return _willAdd;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_willAdd);
  }

  final List<String> _willFill;
  @override
  List<String> get willFill {
    if (_willFill is EqualUnmodifiableListView) return _willFill;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_willFill);
  }

  final List<String> _willPrune;
  @override
  List<String> get willPrune {
    if (_willPrune is EqualUnmodifiableListView) return _willPrune;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_willPrune);
  }

  final List<String> _willKeep;
  @override
  List<String> get willKeep {
    if (_willKeep is EqualUnmodifiableListView) return _willKeep;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_willKeep);
  }

  @override
  final String? warnings;
  @override
  final bool? canUndo;

  @override
  String toString() {
    return 'MaterializationPreview(parentId: $parentId, willAdd: $willAdd, willFill: $willFill, willPrune: $willPrune, willKeep: $willKeep, warnings: $warnings, canUndo: $canUndo)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$MaterializationPreviewImpl &&
            (identical(other.parentId, parentId) ||
                other.parentId == parentId) &&
            const DeepCollectionEquality().equals(other._willAdd, _willAdd) &&
            const DeepCollectionEquality().equals(other._willFill, _willFill) &&
            const DeepCollectionEquality()
                .equals(other._willPrune, _willPrune) &&
            const DeepCollectionEquality().equals(other._willKeep, _willKeep) &&
            (identical(other.warnings, warnings) ||
                other.warnings == warnings) &&
            (identical(other.canUndo, canUndo) || other.canUndo == canUndo));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      parentId,
      const DeepCollectionEquality().hash(_willAdd),
      const DeepCollectionEquality().hash(_willFill),
      const DeepCollectionEquality().hash(_willPrune),
      const DeepCollectionEquality().hash(_willKeep),
      warnings,
      canUndo);

  /// Create a copy of MaterializationPreview
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$MaterializationPreviewImplCopyWith<_$MaterializationPreviewImpl>
      get copyWith => __$$MaterializationPreviewImplCopyWithImpl<
          _$MaterializationPreviewImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$MaterializationPreviewImplToJson(
      this,
    );
  }
}

abstract class _MaterializationPreview implements MaterializationPreview {
  const factory _MaterializationPreview(
      {required final int parentId,
      required final List<String> willAdd,
      required final List<String> willFill,
      required final List<String> willPrune,
      required final List<String> willKeep,
      final String? warnings,
      final bool? canUndo}) = _$MaterializationPreviewImpl;

  factory _MaterializationPreview.fromJson(Map<String, dynamic> json) =
      _$MaterializationPreviewImpl.fromJson;

  @override
  int get parentId;
  @override
  List<String> get willAdd;
  @override
  List<String> get willFill;
  @override
  List<String> get willPrune;
  @override
  List<String> get willKeep;
  @override
  String? get warnings;
  @override
  bool? get canUndo;

  /// Create a copy of MaterializationPreview
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$MaterializationPreviewImplCopyWith<_$MaterializationPreviewImpl>
      get copyWith => throw _privateConstructorUsedError;
}

MaterializationStats _$MaterializationStatsFromJson(Map<String, dynamic> json) {
  return _MaterializationStats.fromJson(json);
}

/// @nodoc
mixin _$MaterializationStats {
  int get totalMaterializations => throw _privateConstructorUsedError;
  int get totalAdded => throw _privateConstructorUsedError;
  int get totalFilled => throw _privateConstructorUsedError;
  int get totalPruned => throw _privateConstructorUsedError;
  int get totalKept => throw _privateConstructorUsedError;
  DateTime? get lastMaterialization => throw _privateConstructorUsedError;
  Map<String, int>? get byOperationType => throw _privateConstructorUsedError;

  /// Serializes this MaterializationStats to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of MaterializationStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $MaterializationStatsCopyWith<MaterializationStats> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $MaterializationStatsCopyWith<$Res> {
  factory $MaterializationStatsCopyWith(MaterializationStats value,
          $Res Function(MaterializationStats) then) =
      _$MaterializationStatsCopyWithImpl<$Res, MaterializationStats>;
  @useResult
  $Res call(
      {int totalMaterializations,
      int totalAdded,
      int totalFilled,
      int totalPruned,
      int totalKept,
      DateTime? lastMaterialization,
      Map<String, int>? byOperationType});
}

/// @nodoc
class _$MaterializationStatsCopyWithImpl<$Res,
        $Val extends MaterializationStats>
    implements $MaterializationStatsCopyWith<$Res> {
  _$MaterializationStatsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of MaterializationStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalMaterializations = null,
    Object? totalAdded = null,
    Object? totalFilled = null,
    Object? totalPruned = null,
    Object? totalKept = null,
    Object? lastMaterialization = freezed,
    Object? byOperationType = freezed,
  }) {
    return _then(_value.copyWith(
      totalMaterializations: null == totalMaterializations
          ? _value.totalMaterializations
          : totalMaterializations // ignore: cast_nullable_to_non_nullable
              as int,
      totalAdded: null == totalAdded
          ? _value.totalAdded
          : totalAdded // ignore: cast_nullable_to_non_nullable
              as int,
      totalFilled: null == totalFilled
          ? _value.totalFilled
          : totalFilled // ignore: cast_nullable_to_non_nullable
              as int,
      totalPruned: null == totalPruned
          ? _value.totalPruned
          : totalPruned // ignore: cast_nullable_to_non_nullable
              as int,
      totalKept: null == totalKept
          ? _value.totalKept
          : totalKept // ignore: cast_nullable_to_non_nullable
              as int,
      lastMaterialization: freezed == lastMaterialization
          ? _value.lastMaterialization
          : lastMaterialization // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      byOperationType: freezed == byOperationType
          ? _value.byOperationType
          : byOperationType // ignore: cast_nullable_to_non_nullable
              as Map<String, int>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$MaterializationStatsImplCopyWith<$Res>
    implements $MaterializationStatsCopyWith<$Res> {
  factory _$$MaterializationStatsImplCopyWith(_$MaterializationStatsImpl value,
          $Res Function(_$MaterializationStatsImpl) then) =
      __$$MaterializationStatsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int totalMaterializations,
      int totalAdded,
      int totalFilled,
      int totalPruned,
      int totalKept,
      DateTime? lastMaterialization,
      Map<String, int>? byOperationType});
}

/// @nodoc
class __$$MaterializationStatsImplCopyWithImpl<$Res>
    extends _$MaterializationStatsCopyWithImpl<$Res, _$MaterializationStatsImpl>
    implements _$$MaterializationStatsImplCopyWith<$Res> {
  __$$MaterializationStatsImplCopyWithImpl(_$MaterializationStatsImpl _value,
      $Res Function(_$MaterializationStatsImpl) _then)
      : super(_value, _then);

  /// Create a copy of MaterializationStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalMaterializations = null,
    Object? totalAdded = null,
    Object? totalFilled = null,
    Object? totalPruned = null,
    Object? totalKept = null,
    Object? lastMaterialization = freezed,
    Object? byOperationType = freezed,
  }) {
    return _then(_$MaterializationStatsImpl(
      totalMaterializations: null == totalMaterializations
          ? _value.totalMaterializations
          : totalMaterializations // ignore: cast_nullable_to_non_nullable
              as int,
      totalAdded: null == totalAdded
          ? _value.totalAdded
          : totalAdded // ignore: cast_nullable_to_non_nullable
              as int,
      totalFilled: null == totalFilled
          ? _value.totalFilled
          : totalFilled // ignore: cast_nullable_to_non_nullable
              as int,
      totalPruned: null == totalPruned
          ? _value.totalPruned
          : totalPruned // ignore: cast_nullable_to_non_nullable
              as int,
      totalKept: null == totalKept
          ? _value.totalKept
          : totalKept // ignore: cast_nullable_to_non_nullable
              as int,
      lastMaterialization: freezed == lastMaterialization
          ? _value.lastMaterialization
          : lastMaterialization // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      byOperationType: freezed == byOperationType
          ? _value._byOperationType
          : byOperationType // ignore: cast_nullable_to_non_nullable
              as Map<String, int>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$MaterializationStatsImpl implements _MaterializationStats {
  const _$MaterializationStatsImpl(
      {required this.totalMaterializations,
      required this.totalAdded,
      required this.totalFilled,
      required this.totalPruned,
      required this.totalKept,
      this.lastMaterialization,
      final Map<String, int>? byOperationType})
      : _byOperationType = byOperationType;

  factory _$MaterializationStatsImpl.fromJson(Map<String, dynamic> json) =>
      _$$MaterializationStatsImplFromJson(json);

  @override
  final int totalMaterializations;
  @override
  final int totalAdded;
  @override
  final int totalFilled;
  @override
  final int totalPruned;
  @override
  final int totalKept;
  @override
  final DateTime? lastMaterialization;
  final Map<String, int>? _byOperationType;
  @override
  Map<String, int>? get byOperationType {
    final value = _byOperationType;
    if (value == null) return null;
    if (_byOperationType is EqualUnmodifiableMapView) return _byOperationType;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'MaterializationStats(totalMaterializations: $totalMaterializations, totalAdded: $totalAdded, totalFilled: $totalFilled, totalPruned: $totalPruned, totalKept: $totalKept, lastMaterialization: $lastMaterialization, byOperationType: $byOperationType)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$MaterializationStatsImpl &&
            (identical(other.totalMaterializations, totalMaterializations) ||
                other.totalMaterializations == totalMaterializations) &&
            (identical(other.totalAdded, totalAdded) ||
                other.totalAdded == totalAdded) &&
            (identical(other.totalFilled, totalFilled) ||
                other.totalFilled == totalFilled) &&
            (identical(other.totalPruned, totalPruned) ||
                other.totalPruned == totalPruned) &&
            (identical(other.totalKept, totalKept) ||
                other.totalKept == totalKept) &&
            (identical(other.lastMaterialization, lastMaterialization) ||
                other.lastMaterialization == lastMaterialization) &&
            const DeepCollectionEquality()
                .equals(other._byOperationType, _byOperationType));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      totalMaterializations,
      totalAdded,
      totalFilled,
      totalPruned,
      totalKept,
      lastMaterialization,
      const DeepCollectionEquality().hash(_byOperationType));

  /// Create a copy of MaterializationStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$MaterializationStatsImplCopyWith<_$MaterializationStatsImpl>
      get copyWith =>
          __$$MaterializationStatsImplCopyWithImpl<_$MaterializationStatsImpl>(
              this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$MaterializationStatsImplToJson(
      this,
    );
  }
}

abstract class _MaterializationStats implements MaterializationStats {
  const factory _MaterializationStats(
      {required final int totalMaterializations,
      required final int totalAdded,
      required final int totalFilled,
      required final int totalPruned,
      required final int totalKept,
      final DateTime? lastMaterialization,
      final Map<String, int>? byOperationType}) = _$MaterializationStatsImpl;

  factory _MaterializationStats.fromJson(Map<String, dynamic> json) =
      _$MaterializationStatsImpl.fromJson;

  @override
  int get totalMaterializations;
  @override
  int get totalAdded;
  @override
  int get totalFilled;
  @override
  int get totalPruned;
  @override
  int get totalKept;
  @override
  DateTime? get lastMaterialization;
  @override
  Map<String, int>? get byOperationType;

  /// Create a copy of MaterializationStats
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$MaterializationStatsImplCopyWith<_$MaterializationStatsImpl>
      get copyWith => throw _privateConstructorUsedError;
}
