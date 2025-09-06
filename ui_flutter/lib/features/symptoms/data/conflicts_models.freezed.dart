// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'conflicts_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

ConflictItem _$ConflictItemFromJson(Map<String, dynamic> json) {
  return _ConflictItem.fromJson(json);
}

/// @nodoc
mixin _$ConflictItem {
  int get id => throw _privateConstructorUsedError;
  ConflictType get type => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  List<int> get affectedNodes => throw _privateConstructorUsedError;
  List<String> get affectedLabels => throw _privateConstructorUsedError;
  int? get parentId => throw _privateConstructorUsedError;
  int? get depth => throw _privateConstructorUsedError;
  String? get resolution => throw _privateConstructorUsedError;
  DateTime? get detectedAt => throw _privateConstructorUsedError;

  /// Serializes this ConflictItem to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConflictItem
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConflictItemCopyWith<ConflictItem> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConflictItemCopyWith<$Res> {
  factory $ConflictItemCopyWith(
          ConflictItem value, $Res Function(ConflictItem) then) =
      _$ConflictItemCopyWithImpl<$Res, ConflictItem>;
  @useResult
  $Res call(
      {int id,
      ConflictType type,
      String description,
      List<int> affectedNodes,
      List<String> affectedLabels,
      int? parentId,
      int? depth,
      String? resolution,
      DateTime? detectedAt});
}

/// @nodoc
class _$ConflictItemCopyWithImpl<$Res, $Val extends ConflictItem>
    implements $ConflictItemCopyWith<$Res> {
  _$ConflictItemCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConflictItem
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? type = null,
    Object? description = null,
    Object? affectedNodes = null,
    Object? affectedLabels = null,
    Object? parentId = freezed,
    Object? depth = freezed,
    Object? resolution = freezed,
    Object? detectedAt = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as ConflictType,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      affectedNodes: null == affectedNodes
          ? _value.affectedNodes
          : affectedNodes // ignore: cast_nullable_to_non_nullable
              as List<int>,
      affectedLabels: null == affectedLabels
          ? _value.affectedLabels
          : affectedLabels // ignore: cast_nullable_to_non_nullable
              as List<String>,
      parentId: freezed == parentId
          ? _value.parentId
          : parentId // ignore: cast_nullable_to_non_nullable
              as int?,
      depth: freezed == depth
          ? _value.depth
          : depth // ignore: cast_nullable_to_non_nullable
              as int?,
      resolution: freezed == resolution
          ? _value.resolution
          : resolution // ignore: cast_nullable_to_non_nullable
              as String?,
      detectedAt: freezed == detectedAt
          ? _value.detectedAt
          : detectedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ConflictItemImplCopyWith<$Res>
    implements $ConflictItemCopyWith<$Res> {
  factory _$$ConflictItemImplCopyWith(
          _$ConflictItemImpl value, $Res Function(_$ConflictItemImpl) then) =
      __$$ConflictItemImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id,
      ConflictType type,
      String description,
      List<int> affectedNodes,
      List<String> affectedLabels,
      int? parentId,
      int? depth,
      String? resolution,
      DateTime? detectedAt});
}

/// @nodoc
class __$$ConflictItemImplCopyWithImpl<$Res>
    extends _$ConflictItemCopyWithImpl<$Res, _$ConflictItemImpl>
    implements _$$ConflictItemImplCopyWith<$Res> {
  __$$ConflictItemImplCopyWithImpl(
      _$ConflictItemImpl _value, $Res Function(_$ConflictItemImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConflictItem
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? type = null,
    Object? description = null,
    Object? affectedNodes = null,
    Object? affectedLabels = null,
    Object? parentId = freezed,
    Object? depth = freezed,
    Object? resolution = freezed,
    Object? detectedAt = freezed,
  }) {
    return _then(_$ConflictItemImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as ConflictType,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      affectedNodes: null == affectedNodes
          ? _value._affectedNodes
          : affectedNodes // ignore: cast_nullable_to_non_nullable
              as List<int>,
      affectedLabels: null == affectedLabels
          ? _value._affectedLabels
          : affectedLabels // ignore: cast_nullable_to_non_nullable
              as List<String>,
      parentId: freezed == parentId
          ? _value.parentId
          : parentId // ignore: cast_nullable_to_non_nullable
              as int?,
      depth: freezed == depth
          ? _value.depth
          : depth // ignore: cast_nullable_to_non_nullable
              as int?,
      resolution: freezed == resolution
          ? _value.resolution
          : resolution // ignore: cast_nullable_to_non_nullable
              as String?,
      detectedAt: freezed == detectedAt
          ? _value.detectedAt
          : detectedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConflictItemImpl implements _ConflictItem {
  const _$ConflictItemImpl(
      {required this.id,
      required this.type,
      required this.description,
      required final List<int> affectedNodes,
      required final List<String> affectedLabels,
      this.parentId,
      this.depth,
      this.resolution,
      this.detectedAt})
      : _affectedNodes = affectedNodes,
        _affectedLabels = affectedLabels;

  factory _$ConflictItemImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConflictItemImplFromJson(json);

  @override
  final int id;
  @override
  final ConflictType type;
  @override
  final String description;
  final List<int> _affectedNodes;
  @override
  List<int> get affectedNodes {
    if (_affectedNodes is EqualUnmodifiableListView) return _affectedNodes;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_affectedNodes);
  }

  final List<String> _affectedLabels;
  @override
  List<String> get affectedLabels {
    if (_affectedLabels is EqualUnmodifiableListView) return _affectedLabels;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_affectedLabels);
  }

  @override
  final int? parentId;
  @override
  final int? depth;
  @override
  final String? resolution;
  @override
  final DateTime? detectedAt;

  @override
  String toString() {
    return 'ConflictItem(id: $id, type: $type, description: $description, affectedNodes: $affectedNodes, affectedLabels: $affectedLabels, parentId: $parentId, depth: $depth, resolution: $resolution, detectedAt: $detectedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConflictItemImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.description, description) ||
                other.description == description) &&
            const DeepCollectionEquality()
                .equals(other._affectedNodes, _affectedNodes) &&
            const DeepCollectionEquality()
                .equals(other._affectedLabels, _affectedLabels) &&
            (identical(other.parentId, parentId) ||
                other.parentId == parentId) &&
            (identical(other.depth, depth) || other.depth == depth) &&
            (identical(other.resolution, resolution) ||
                other.resolution == resolution) &&
            (identical(other.detectedAt, detectedAt) ||
                other.detectedAt == detectedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      type,
      description,
      const DeepCollectionEquality().hash(_affectedNodes),
      const DeepCollectionEquality().hash(_affectedLabels),
      parentId,
      depth,
      resolution,
      detectedAt);

  /// Create a copy of ConflictItem
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConflictItemImplCopyWith<_$ConflictItemImpl> get copyWith =>
      __$$ConflictItemImplCopyWithImpl<_$ConflictItemImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConflictItemImplToJson(
      this,
    );
  }
}

abstract class _ConflictItem implements ConflictItem {
  const factory _ConflictItem(
      {required final int id,
      required final ConflictType type,
      required final String description,
      required final List<int> affectedNodes,
      required final List<String> affectedLabels,
      final int? parentId,
      final int? depth,
      final String? resolution,
      final DateTime? detectedAt}) = _$ConflictItemImpl;

  factory _ConflictItem.fromJson(Map<String, dynamic> json) =
      _$ConflictItemImpl.fromJson;

  @override
  int get id;
  @override
  ConflictType get type;
  @override
  String get description;
  @override
  List<int> get affectedNodes;
  @override
  List<String> get affectedLabels;
  @override
  int? get parentId;
  @override
  int? get depth;
  @override
  String? get resolution;
  @override
  DateTime? get detectedAt;

  /// Create a copy of ConflictItem
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConflictItemImplCopyWith<_$ConflictItemImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ConflictGroup _$ConflictGroupFromJson(Map<String, dynamic> json) {
  return _ConflictGroup.fromJson(json);
}

/// @nodoc
mixin _$ConflictGroup {
  ConflictType get type => throw _privateConstructorUsedError;
  List<ConflictItem> get items => throw _privateConstructorUsedError;
  int get totalCount => throw _privateConstructorUsedError;
  String? get summary => throw _privateConstructorUsedError;

  /// Serializes this ConflictGroup to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConflictGroup
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConflictGroupCopyWith<ConflictGroup> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConflictGroupCopyWith<$Res> {
  factory $ConflictGroupCopyWith(
          ConflictGroup value, $Res Function(ConflictGroup) then) =
      _$ConflictGroupCopyWithImpl<$Res, ConflictGroup>;
  @useResult
  $Res call(
      {ConflictType type,
      List<ConflictItem> items,
      int totalCount,
      String? summary});
}

/// @nodoc
class _$ConflictGroupCopyWithImpl<$Res, $Val extends ConflictGroup>
    implements $ConflictGroupCopyWith<$Res> {
  _$ConflictGroupCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConflictGroup
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? type = null,
    Object? items = null,
    Object? totalCount = null,
    Object? summary = freezed,
  }) {
    return _then(_value.copyWith(
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as ConflictType,
      items: null == items
          ? _value.items
          : items // ignore: cast_nullable_to_non_nullable
              as List<ConflictItem>,
      totalCount: null == totalCount
          ? _value.totalCount
          : totalCount // ignore: cast_nullable_to_non_nullable
              as int,
      summary: freezed == summary
          ? _value.summary
          : summary // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ConflictGroupImplCopyWith<$Res>
    implements $ConflictGroupCopyWith<$Res> {
  factory _$$ConflictGroupImplCopyWith(
          _$ConflictGroupImpl value, $Res Function(_$ConflictGroupImpl) then) =
      __$$ConflictGroupImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {ConflictType type,
      List<ConflictItem> items,
      int totalCount,
      String? summary});
}

/// @nodoc
class __$$ConflictGroupImplCopyWithImpl<$Res>
    extends _$ConflictGroupCopyWithImpl<$Res, _$ConflictGroupImpl>
    implements _$$ConflictGroupImplCopyWith<$Res> {
  __$$ConflictGroupImplCopyWithImpl(
      _$ConflictGroupImpl _value, $Res Function(_$ConflictGroupImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConflictGroup
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? type = null,
    Object? items = null,
    Object? totalCount = null,
    Object? summary = freezed,
  }) {
    return _then(_$ConflictGroupImpl(
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as ConflictType,
      items: null == items
          ? _value._items
          : items // ignore: cast_nullable_to_non_nullable
              as List<ConflictItem>,
      totalCount: null == totalCount
          ? _value.totalCount
          : totalCount // ignore: cast_nullable_to_non_nullable
              as int,
      summary: freezed == summary
          ? _value.summary
          : summary // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConflictGroupImpl implements _ConflictGroup {
  const _$ConflictGroupImpl(
      {required this.type,
      required final List<ConflictItem> items,
      required this.totalCount,
      this.summary})
      : _items = items;

  factory _$ConflictGroupImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConflictGroupImplFromJson(json);

  @override
  final ConflictType type;
  final List<ConflictItem> _items;
  @override
  List<ConflictItem> get items {
    if (_items is EqualUnmodifiableListView) return _items;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_items);
  }

  @override
  final int totalCount;
  @override
  final String? summary;

  @override
  String toString() {
    return 'ConflictGroup(type: $type, items: $items, totalCount: $totalCount, summary: $summary)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConflictGroupImpl &&
            (identical(other.type, type) || other.type == type) &&
            const DeepCollectionEquality().equals(other._items, _items) &&
            (identical(other.totalCount, totalCount) ||
                other.totalCount == totalCount) &&
            (identical(other.summary, summary) || other.summary == summary));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, type,
      const DeepCollectionEquality().hash(_items), totalCount, summary);

  /// Create a copy of ConflictGroup
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConflictGroupImplCopyWith<_$ConflictGroupImpl> get copyWith =>
      __$$ConflictGroupImplCopyWithImpl<_$ConflictGroupImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConflictGroupImplToJson(
      this,
    );
  }
}

abstract class _ConflictGroup implements ConflictGroup {
  const factory _ConflictGroup(
      {required final ConflictType type,
      required final List<ConflictItem> items,
      required final int totalCount,
      final String? summary}) = _$ConflictGroupImpl;

  factory _ConflictGroup.fromJson(Map<String, dynamic> json) =
      _$ConflictGroupImpl.fromJson;

  @override
  ConflictType get type;
  @override
  List<ConflictItem> get items;
  @override
  int get totalCount;
  @override
  String? get summary;

  /// Create a copy of ConflictGroup
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConflictGroupImplCopyWith<_$ConflictGroupImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ConflictsReport _$ConflictsReportFromJson(Map<String, dynamic> json) {
  return _ConflictsReport.fromJson(json);
}

/// @nodoc
mixin _$ConflictsReport {
  List<ConflictGroup> get groups => throw _privateConstructorUsedError;
  int get totalConflicts => throw _privateConstructorUsedError;
  DateTime? get generatedAt => throw _privateConstructorUsedError;
  Map<String, int>? get byType => throw _privateConstructorUsedError;

  /// Serializes this ConflictsReport to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConflictsReport
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConflictsReportCopyWith<ConflictsReport> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConflictsReportCopyWith<$Res> {
  factory $ConflictsReportCopyWith(
          ConflictsReport value, $Res Function(ConflictsReport) then) =
      _$ConflictsReportCopyWithImpl<$Res, ConflictsReport>;
  @useResult
  $Res call(
      {List<ConflictGroup> groups,
      int totalConflicts,
      DateTime? generatedAt,
      Map<String, int>? byType});
}

/// @nodoc
class _$ConflictsReportCopyWithImpl<$Res, $Val extends ConflictsReport>
    implements $ConflictsReportCopyWith<$Res> {
  _$ConflictsReportCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConflictsReport
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? groups = null,
    Object? totalConflicts = null,
    Object? generatedAt = freezed,
    Object? byType = freezed,
  }) {
    return _then(_value.copyWith(
      groups: null == groups
          ? _value.groups
          : groups // ignore: cast_nullable_to_non_nullable
              as List<ConflictGroup>,
      totalConflicts: null == totalConflicts
          ? _value.totalConflicts
          : totalConflicts // ignore: cast_nullable_to_non_nullable
              as int,
      generatedAt: freezed == generatedAt
          ? _value.generatedAt
          : generatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      byType: freezed == byType
          ? _value.byType
          : byType // ignore: cast_nullable_to_non_nullable
              as Map<String, int>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ConflictsReportImplCopyWith<$Res>
    implements $ConflictsReportCopyWith<$Res> {
  factory _$$ConflictsReportImplCopyWith(_$ConflictsReportImpl value,
          $Res Function(_$ConflictsReportImpl) then) =
      __$$ConflictsReportImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {List<ConflictGroup> groups,
      int totalConflicts,
      DateTime? generatedAt,
      Map<String, int>? byType});
}

/// @nodoc
class __$$ConflictsReportImplCopyWithImpl<$Res>
    extends _$ConflictsReportCopyWithImpl<$Res, _$ConflictsReportImpl>
    implements _$$ConflictsReportImplCopyWith<$Res> {
  __$$ConflictsReportImplCopyWithImpl(
      _$ConflictsReportImpl _value, $Res Function(_$ConflictsReportImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConflictsReport
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? groups = null,
    Object? totalConflicts = null,
    Object? generatedAt = freezed,
    Object? byType = freezed,
  }) {
    return _then(_$ConflictsReportImpl(
      groups: null == groups
          ? _value._groups
          : groups // ignore: cast_nullable_to_non_nullable
              as List<ConflictGroup>,
      totalConflicts: null == totalConflicts
          ? _value.totalConflicts
          : totalConflicts // ignore: cast_nullable_to_non_nullable
              as int,
      generatedAt: freezed == generatedAt
          ? _value.generatedAt
          : generatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      byType: freezed == byType
          ? _value._byType
          : byType // ignore: cast_nullable_to_non_nullable
              as Map<String, int>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConflictsReportImpl implements _ConflictsReport {
  const _$ConflictsReportImpl(
      {required final List<ConflictGroup> groups,
      required this.totalConflicts,
      this.generatedAt,
      final Map<String, int>? byType})
      : _groups = groups,
        _byType = byType;

  factory _$ConflictsReportImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConflictsReportImplFromJson(json);

  final List<ConflictGroup> _groups;
  @override
  List<ConflictGroup> get groups {
    if (_groups is EqualUnmodifiableListView) return _groups;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_groups);
  }

  @override
  final int totalConflicts;
  @override
  final DateTime? generatedAt;
  final Map<String, int>? _byType;
  @override
  Map<String, int>? get byType {
    final value = _byType;
    if (value == null) return null;
    if (_byType is EqualUnmodifiableMapView) return _byType;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'ConflictsReport(groups: $groups, totalConflicts: $totalConflicts, generatedAt: $generatedAt, byType: $byType)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConflictsReportImpl &&
            const DeepCollectionEquality().equals(other._groups, _groups) &&
            (identical(other.totalConflicts, totalConflicts) ||
                other.totalConflicts == totalConflicts) &&
            (identical(other.generatedAt, generatedAt) ||
                other.generatedAt == generatedAt) &&
            const DeepCollectionEquality().equals(other._byType, _byType));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_groups),
      totalConflicts,
      generatedAt,
      const DeepCollectionEquality().hash(_byType));

  /// Create a copy of ConflictsReport
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConflictsReportImplCopyWith<_$ConflictsReportImpl> get copyWith =>
      __$$ConflictsReportImplCopyWithImpl<_$ConflictsReportImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConflictsReportImplToJson(
      this,
    );
  }
}

abstract class _ConflictsReport implements ConflictsReport {
  const factory _ConflictsReport(
      {required final List<ConflictGroup> groups,
      required final int totalConflicts,
      final DateTime? generatedAt,
      final Map<String, int>? byType}) = _$ConflictsReportImpl;

  factory _ConflictsReport.fromJson(Map<String, dynamic> json) =
      _$ConflictsReportImpl.fromJson;

  @override
  List<ConflictGroup> get groups;
  @override
  int get totalConflicts;
  @override
  DateTime? get generatedAt;
  @override
  Map<String, int>? get byType;

  /// Create a copy of ConflictsReport
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConflictsReportImplCopyWith<_$ConflictsReportImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ConflictResolution _$ConflictResolutionFromJson(Map<String, dynamic> json) {
  return _ConflictResolution.fromJson(json);
}

/// @nodoc
mixin _$ConflictResolution {
  int get conflictId => throw _privateConstructorUsedError;
  String get action => throw _privateConstructorUsedError;
  String? get newValue => throw _privateConstructorUsedError;
  Map<String, dynamic>? get metadata => throw _privateConstructorUsedError;

  /// Serializes this ConflictResolution to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ConflictResolution
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ConflictResolutionCopyWith<ConflictResolution> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ConflictResolutionCopyWith<$Res> {
  factory $ConflictResolutionCopyWith(
          ConflictResolution value, $Res Function(ConflictResolution) then) =
      _$ConflictResolutionCopyWithImpl<$Res, ConflictResolution>;
  @useResult
  $Res call(
      {int conflictId,
      String action,
      String? newValue,
      Map<String, dynamic>? metadata});
}

/// @nodoc
class _$ConflictResolutionCopyWithImpl<$Res, $Val extends ConflictResolution>
    implements $ConflictResolutionCopyWith<$Res> {
  _$ConflictResolutionCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ConflictResolution
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? conflictId = null,
    Object? action = null,
    Object? newValue = freezed,
    Object? metadata = freezed,
  }) {
    return _then(_value.copyWith(
      conflictId: null == conflictId
          ? _value.conflictId
          : conflictId // ignore: cast_nullable_to_non_nullable
              as int,
      action: null == action
          ? _value.action
          : action // ignore: cast_nullable_to_non_nullable
              as String,
      newValue: freezed == newValue
          ? _value.newValue
          : newValue // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: freezed == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ConflictResolutionImplCopyWith<$Res>
    implements $ConflictResolutionCopyWith<$Res> {
  factory _$$ConflictResolutionImplCopyWith(_$ConflictResolutionImpl value,
          $Res Function(_$ConflictResolutionImpl) then) =
      __$$ConflictResolutionImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int conflictId,
      String action,
      String? newValue,
      Map<String, dynamic>? metadata});
}

/// @nodoc
class __$$ConflictResolutionImplCopyWithImpl<$Res>
    extends _$ConflictResolutionCopyWithImpl<$Res, _$ConflictResolutionImpl>
    implements _$$ConflictResolutionImplCopyWith<$Res> {
  __$$ConflictResolutionImplCopyWithImpl(_$ConflictResolutionImpl _value,
      $Res Function(_$ConflictResolutionImpl) _then)
      : super(_value, _then);

  /// Create a copy of ConflictResolution
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? conflictId = null,
    Object? action = null,
    Object? newValue = freezed,
    Object? metadata = freezed,
  }) {
    return _then(_$ConflictResolutionImpl(
      conflictId: null == conflictId
          ? _value.conflictId
          : conflictId // ignore: cast_nullable_to_non_nullable
              as int,
      action: null == action
          ? _value.action
          : action // ignore: cast_nullable_to_non_nullable
              as String,
      newValue: freezed == newValue
          ? _value.newValue
          : newValue // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: freezed == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ConflictResolutionImpl implements _ConflictResolution {
  const _$ConflictResolutionImpl(
      {required this.conflictId,
      required this.action,
      this.newValue,
      final Map<String, dynamic>? metadata})
      : _metadata = metadata;

  factory _$ConflictResolutionImpl.fromJson(Map<String, dynamic> json) =>
      _$$ConflictResolutionImplFromJson(json);

  @override
  final int conflictId;
  @override
  final String action;
  @override
  final String? newValue;
  final Map<String, dynamic>? _metadata;
  @override
  Map<String, dynamic>? get metadata {
    final value = _metadata;
    if (value == null) return null;
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'ConflictResolution(conflictId: $conflictId, action: $action, newValue: $newValue, metadata: $metadata)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ConflictResolutionImpl &&
            (identical(other.conflictId, conflictId) ||
                other.conflictId == conflictId) &&
            (identical(other.action, action) || other.action == action) &&
            (identical(other.newValue, newValue) ||
                other.newValue == newValue) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, conflictId, action, newValue,
      const DeepCollectionEquality().hash(_metadata));

  /// Create a copy of ConflictResolution
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ConflictResolutionImplCopyWith<_$ConflictResolutionImpl> get copyWith =>
      __$$ConflictResolutionImplCopyWithImpl<_$ConflictResolutionImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ConflictResolutionImplToJson(
      this,
    );
  }
}

abstract class _ConflictResolution implements ConflictResolution {
  const factory _ConflictResolution(
      {required final int conflictId,
      required final String action,
      final String? newValue,
      final Map<String, dynamic>? metadata}) = _$ConflictResolutionImpl;

  factory _ConflictResolution.fromJson(Map<String, dynamic> json) =
      _$ConflictResolutionImpl.fromJson;

  @override
  int get conflictId;
  @override
  String get action;
  @override
  String? get newValue;
  @override
  Map<String, dynamic>? get metadata;

  /// Create a copy of ConflictResolution
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ConflictResolutionImplCopyWith<_$ConflictResolutionImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
